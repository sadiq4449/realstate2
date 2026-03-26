import { useState } from "react";

/** Simple carousel for listing thumbnails with keyboard-friendly dots. */
export function ImageSlider({ images, alt }: { images: string[]; alt: string }) {
  const [i, setI] = useState(0);
  const list = images.length
    ? images
    : ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800"];
  const src = list[i % list.length];
  return (
    <div className="relative group rounded-xl overflow-hidden bg-gray-200 aspect-[16/10]">
      <img src={src} alt={alt} className="w-full h-full object-cover" />
      {list.length > 1 && (
        <>
          <button
            type="button"
            aria-label="Previous image"
            className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white px-2 py-1 rounded-md text-sm opacity-0 group-hover:opacity-100 transition"
            onClick={() => setI((x) => (x - 1 + list.length) % list.length)}
          >
            ‹
          </button>
          <button
            type="button"
            aria-label="Next image"
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white px-2 py-1 rounded-md text-sm opacity-0 group-hover:opacity-100 transition"
            onClick={() => setI((x) => (x + 1) % list.length)}
          >
            ›
          </button>
        </>
      )}
    </div>
  );
}
