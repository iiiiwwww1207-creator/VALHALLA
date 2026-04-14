import { notFound } from 'next/navigation';
import { HostProfile } from '@/components/hosts/host-profile';
import { hosts } from '@/data/hosts';

export default async function HostProfilePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const host = hosts.find((entry) => entry.id === id);

  if (!host) {
    notFound();
  }

  return <HostProfile host={host} />;
}
