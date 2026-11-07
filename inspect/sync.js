// Cloud sync with a Supabase project (tables and policies in supabase/schema.sql). The device stays the working
// copy: changes are pushed from the outbox, then newer rows from other devices are pulled. Only the project URL and
// the publishable (anon) key live in the browser; rows are protected by row-level security for signed-in users.
import { createClient } from '@supabase/supabase-js';
import * as store from './store.js';

const BUCKET = 'defect-photos';
const LOCAL_ONLY = { photos: ['blob', 'uploaded'] };
const TABLE = { inspections: 'inspections', defects: 'defects', photos: 'defect_photos' };

export class Cloud {
  constructor() { this.client = null; this.config = null; }

  configure(config) {
    const ok = config?.url && config?.key;
    if (!ok) { this.client = null; this.config = null; return false; }
    if (this.config?.url === config.url && this.config?.key === config.key) return true;
    this.config = { url: config.url.trim().replace(/\/+$/, ''), key: config.key.trim() };
    this.client = createClient(this.config.url, this.config.key, {
      auth: { persistSession: true, autoRefreshToken: true, storageKey: 'bridge-inspection-auth' },
    });
    return true;
  }

  get ready() { return !!this.client; }

  async user() {
    if (!this.client) return null;
    const { data } = await this.client.auth.getSession();
    return data.session?.user || null;
  }

  async signIn(email, password) {
    const { error } = await this.client.auth.signInWithPassword({ email, password });
    if (error) throw error;
  }

  async signOut() { await this.client?.auth.signOut(); }

  row(storeName, record) {
    const out = { ...record };
    for (const key of LOCAL_ONLY[storeName] || []) delete out[key];
    return out;
  }

  // Push every queued record (inspections, then defects, then photos so foreign keys exist), then pull.
  async sync(bridge, onProgress = () => {}) {
    if (!this.client) throw Error('Cloud sync is not set up.');
    if (!(await this.user())) throw Error('Sign in to sync.');
    const queue = await store.outbox();
    const byStore = { inspections: [], defects: [], photos: [] };
    for (const item of queue) byStore[item.store]?.push(item);
    let pushed = 0;
    for (const name of ['inspections', 'defects', 'photos']) {
      const items = byStore[name];
      if (!items.length) continue;
      const records = (await Promise.all(items.map(i => store.get(name, i.id)))).filter(Boolean);
      if (name === 'photos') {
        for (const photo of records) {
          if (photo.blob && !photo.uploaded) {
            onProgress(`Uploading photo ${photo.file_name}…`);
            const path = `${photo.inspection_id}/${photo.defect_id}/${photo.id}.jpg`;
            const { error } = await this.client.storage.from(BUCKET).upload(path, photo.blob, { contentType: 'image/jpeg', upsert: true });
            if (error) throw Error(`Photo upload failed: ${error.message}`);
            photo.storage_path = path;
            photo.uploaded = true;
            await store.put('photos', photo, { queue: false });
          }
        }
      }
      onProgress(`Sending ${records.length} ${name}…`);
      const { error } = await this.client.from(TABLE[name]).upsert(records.map(r => this.row(name, r)), { defaultToNull: false });
      if (error) throw Error(`Could not send ${name}: ${error.message}`);
      await store.clearOutbox(items.map(i => i.key));
      pushed += records.length;
    }
    const pulled = await this.pull(bridge, onProgress);
    await store.setting('last_sync', new Date().toISOString());
    return { pushed, pulled };
  }

  async pull(bridge, onProgress) {
    const sinceKey = `pulled:${bridge}`;
    const since = (await store.setting(sinceKey)) || '1970-01-01T00:00:00Z';
    const started = new Date().toISOString();
    onProgress('Fetching changes…');
    const take = async (table, filter) => {
      const { data, error } = await filter(this.client.from(table).select('*').gt('synced_at', since));
      if (error) throw Error(`Could not fetch ${table}: ${error.message}`);
      return data;
    };
    const inspections = await take('inspections', q => q.eq('bridge_id', bridge));
    const defects = await take('defects', q => q.eq('bridge_id', bridge));
    const ids = [...new Set([...(await store.inspections(bridge)).map(i => i.id), ...inspections.map(i => i.id)])];
    const photos = ids.length ? await take('defect_photos', q => q.in('inspection_id', ids)) : [];
    const pending = new Set((await store.outbox()).map(o => o.key));
    let count = 0;
    for (const [name, rows] of [['inspections', inspections], ['defects', defects], ['photos', photos]]) {
      const keep = [];
      for (const remote of rows) {
        const local = await store.get(name, remote.id);
        if (pending.has(`${name}:${remote.id}`)) continue;            // local edits win until they are sent
        if (local && local.updated_at > remote.updated_at) continue;
        delete remote.synced_at;
        keep.push(name === 'photos' ? { ...remote, blob: local?.blob || null, uploaded: true } : remote);
      }
      if (keep.length) await store.put(name, keep, { queue: false });
      count += keep.length;
    }
    await store.setting(sinceKey, started);
    return count;
  }

  // Photos taken on another device are fetched when first shown, then kept on this device.
  async photoBlob(photo) {
    if (photo.blob || !photo.storage_path || !this.client) return photo.blob || null;
    const { data, error } = await this.client.storage.from(BUCKET).download(photo.storage_path);
    if (error) return null;
    photo.blob = data;
    await store.put('photos', photo, { queue: false });
    return data;
  }
}
