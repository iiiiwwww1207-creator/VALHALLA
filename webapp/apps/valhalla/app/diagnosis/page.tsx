import { DiagnosisFlow } from '@/components/diagnosis/diagnosis-flow';
import type { DiagnosisRoute } from '@yggdra/shared';

export const dynamic = 'force-static';

export default function DiagnosisPage() {
  const diagnosisRoute: DiagnosisRoute = 'route2';

  return <DiagnosisFlow route={diagnosisRoute} />;
}
