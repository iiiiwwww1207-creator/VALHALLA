import { DiagnosisFlow } from '@/components/diagnosis/diagnosis-flow';

export const dynamic = 'force-static';

export default function DiagnosisPage() {
  const diagnosisRoute = 'route2' as const;

  return <DiagnosisFlow route={diagnosisRoute} />;
}
