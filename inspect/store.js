// Local inspection store (IndexedDB). Everything is saved on the device first; records changed since the last
// cloud sync are listed in the outbox. The 3D viewer page reads the same database (same origin).

const DB_NAME = 'bridge-inspection';
const VERSION = 1;
let opening = null;

export function uuid() {
  if (globalThis.crypto?.randomUUID) return crypto.randomUUID();
  const b = crypto.getRandomValues(new Uint8Array(16));
  b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
  const h = [...b].map(x => x.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

export const now = () => new Date().toISOString();

export function open() {
  if (opening) return opening;
  opening = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      const inspections = db.createObjectStore('inspections', { keyPath: 'id' });
      inspections.createIndex('bridge_id', 'bridge_id');
      const defects = db.createObjectStore('defects', { keyPath: 'id' });
      defects.createIndex('inspection_id', 'inspection_id');
      defects.createIndex('bridge_id', 'bridge_id');
      const photos = db.createObjectStore('photos', { keyPath: 'id' });
      photos.createIndex('defect_id', 'defect_id');
      photos.createIndex('inspection_id', 'inspection_id');
      db.createObjectStore('outbox', { keyPath: 'key' });
      db.createObjectStore('settings');
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
    req.onblocked = () => reject(Error('Close other tabs of this app to upgrade its local database.'));
  });
  return opening;
}

const done = req => new Promise((resolve, reject) => { req.onsuccess = () => resolve(req.result); req.onerror = () => reject(req.error); });

async function tx(stores, mode, fn) {
  const db = await open();
  return new Promise((resolve, reject) => {
    const t = db.transaction(stores, mode);
    let result;
    Promise.resolve(fn(t)).then(r => { result = r; }, reject);
    t.oncomplete = () => resolve(result);
    t.onerror = () => reject(t.error);
    t.onabort = () => reject(t.error || Error('Transaction aborted'));
  });
}

export const get = (store, key) => tx([store], 'readonly', t => done(t.objectStore(store).get(key)));
export const all = (store, index, value) => tx([store], 'readonly', t => {
  const s = t.objectStore(store);
  return done(index ? s.index(index).getAll(value) : s.getAll());
});

// Save records and queue them for sync, in one transaction.
export function put(store, records, { queue = true } = {}) {
  const list = Array.isArray(records) ? records : [records];
  return tx([store, 'outbox'], 'readwrite', t => {
    for (const r of list) {
      t.objectStore(store).put(r);
      if (queue) t.objectStore('outbox').put({ key: `${store}:${r.id}`, store, id: r.id, at: now() });
    }
    return list;
  });
}

export const outbox = () => all('outbox');
export const clearOutbox = keys => tx(['outbox'], 'readwrite', t => { for (const k of keys) t.objectStore('outbox').delete(k); });
export const setting = (key, value) => value === undefined
  ? tx(['settings'], 'readonly', t => done(t.objectStore('settings').get(key)))
  : tx(['settings'], 'readwrite', t => { t.objectStore('settings').put(value, key); });

export const inspections = bridge => all('inspections', 'bridge_id', bridge)
  .then(list => list.sort((a, b) => (b.inspection_date || '').localeCompare(a.inspection_date || '') || b.created_at.localeCompare(a.created_at)));
export const defects = inspection => all('defects', 'inspection_id', inspection).then(list => list.filter(d => !d.deleted).sort((a, b) => a.number - b.number));
export const bridgeDefects = bridge => all('defects', 'bridge_id', bridge).then(list => list.filter(d => !d.deleted));
export const photos = defect => all('photos', 'defect_id', defect).then(list => list.filter(p => !p.deleted).sort((a, b) => a.taken_at.localeCompare(b.taken_at)));
export const inspectionPhotos = inspection => all('photos', 'inspection_id', inspection).then(list => list.filter(p => !p.deleted));
