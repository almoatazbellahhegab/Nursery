/** FEAT-036 groundwork: typed English and Arabic shell messages only. */
export const english = {
  brand: "Nursery",
  heading: "A little care. A big difference.",
  preview: "Development foundation · synthetic preview",
  description:
    "Authentication, organization context and operational records are not connected.",
  overview: "Overview",
  classrooms: "Classrooms",
  empty: "No operational records in this foundation.",
  language: "العربية",
  navigation: "Main navigation",
};
export type Messages = { [Key in keyof typeof english]: string };
export const arabic: Messages = {
  brand: "حضانة",
  heading: "رعاية صغيرة. أثر كبير.",
  preview: "أساس التطوير · معاينة ببيانات تجريبية",
  description: "لم تُربط المصادقة وسياق المؤسسة والسجلات التشغيلية بعد.",
  overview: "نظرة عامة",
  classrooms: "الفصول",
  empty: "لا توجد سجلات تشغيلية في هذه المرحلة.",
  language: "English",
  navigation: "التنقل الرئيسي",
};
