export async function healthCheck(): Promise<{
  status: string;
  resources: Record<string, boolean>;
}> {
  try {
    const res = await fetch('/health');
    if (!res.ok) throw new Error();
    return res.json();
  } catch {
    return { status: 'unreachable', resources: {} };
  }
}
