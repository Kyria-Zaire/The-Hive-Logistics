export function HeroMedia() {
  const videoUrl = process.env.NEXT_PUBLIC_HERO_VIDEO_URL;

  return (
    <div
      className="absolute inset-0 overflow-hidden bg-[var(--bg-primary)]"
      aria-hidden="true"
    >
      {videoUrl ? (
        <video
          className="size-full object-cover"
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          src={videoUrl}
        />
      ) : (
        <div
          className="size-full thl-media-fallback"
          style={{
            background:
              "radial-gradient(ellipse 90% 75% at 72% 42%, var(--bg-secondary) 0%, transparent 62%), linear-gradient(145deg, var(--bg-primary) 12%, var(--bg-secondary) 100%)",
          }}
        />
      )}
    </div>
  );
}
