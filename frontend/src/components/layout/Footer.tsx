export default function Footer() {
  return (
    <footer className="h-12 border-t border-zinc-800 flex items-center justify-center px-6 bg-zinc-950/50">
      <p className="text-xs text-zinc-600">
        &copy; {new Date().getFullYear()} Aether. Next.js, FastAPI & Spring Boot 기반.
      </p>
    </footer>
  );
}
