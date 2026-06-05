export function formatFileSize(bytes) {
  if (bytes === 0) {
    return "0 Bytes";
  }

  const megabytes = bytes / (1024 * 1024);
  return `${megabytes.toFixed(2)} MB`;
}

export function isValidVideoExtension(filename) {
  const allowedExtensions = [".mp4", ".mov", ".avi", ".mkv", ".webm"];

  const extension = filename
    .slice(filename.lastIndexOf("."))
    .toLowerCase();

  return allowedExtensions.includes(extension);
}

export function debounce(fn, delay) {
  let timerId;

  return function (...args) {
    clearTimeout(timerId);

    timerId = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

export function sanitizeHTML(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}