// Field photos: resized on the device (long edge 1920 px, JPEG) and kept in IndexedDB until they are uploaded.
import { uuid, now } from './store.js';

const LONG_EDGE = 1920;

export async function preparePhoto(file, { defect, inspection, sheet, code, number }) {
  const bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' }).catch(() => createImageBitmap(file));
  const scale = Math.min(1, LONG_EDGE / Math.max(bitmap.width, bitmap.height));
  const w = Math.round(bitmap.width * scale), h = Math.round(bitmap.height * scale);
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  canvas.getContext('2d').drawImage(bitmap, 0, 0, w, h);
  bitmap.close?.();
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.84));
  const taken = file.lastModified ? new Date(file.lastModified) : new Date();
  const stamp = taken.toISOString().replace(/[-:]/g, '').replace('T', '_').slice(0, 15);
  const id = uuid();
  return {
    id, defect_id: defect, inspection_id: inspection,
    file_name: `${stamp}_${sheet}_${code}_D${number}_${id.slice(0, 6)}.jpg`,
    taken_at: taken.toISOString(), created_at: now(), updated_at: now(),
    width: w, height: h, bytes: blob.size, caption: '', blob, uploaded: false, deleted: false,
  };
}

const urls = new Map();
export function photoURL(photo) {
  if (!photo.blob) return null;
  if (!urls.has(photo.id)) urls.set(photo.id, URL.createObjectURL(photo.blob));
  return urls.get(photo.id);
}
export function releasePhotoURLs() { for (const u of urls.values()) URL.revokeObjectURL(u); urls.clear(); }
