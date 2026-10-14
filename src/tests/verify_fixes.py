"""
Düzeltme doğrulama scripti — kullanıcının verdiği log'daki BİREBİR veriyle,
offline ve deterministik olarak 3 bug'ın kapandığını test eder.
Ağ/LLM gerektirmez (lab_analyzer joblib'i diskten yükler, fusion saf python).

Çalıştır: python -m src.tests.verify_fixes
"""
from src.schemas.node_schemas.gate_keeper_schemas import LabReport, LabParameter
from src.graph.services.lab_analyzer_service import lab_analyzer_service
from src.graph.services.adaptive_fusion_service import adaptive_fusion_service


def build_lab_report() -> LabReport:
    """Log'daki lab_data'nın birebir kopyası."""
    return LabReport(
        is_valid_report=True,
        patient_age=26,
        patient_gender="MALE",
        patient_blood_type="A_POSITIVE",
        parameters=[
            LabParameter(name="direct_bilirubin", value=4.8, unit="mg/dL", ref_min=0.0, ref_max=0.3, flag="H"),
            LabParameter(name="tot_bilirubin", value=9.2, unit="mg/dL", ref_min=0.2, ref_max=1.2, flag="H"),
            LabParameter(name="AST / SGOT", value=185.0, unit="U/L", ref_min=0.0, ref_max=40.0, flag="H"),
            LabParameter(name="ALT / SGPT", value=210.0, unit="U/L", ref_min=0.0, ref_max=41.0, flag="H"),
            LabParameter(name="alkphos", value=320.0, unit="U/L", ref_min=44.0, ref_max=147.0, flag="H"),
            LabParameter(name="tot_proteins", value=5.1, unit="g/dL", ref_min=6.4, ref_max=8.3, flag="L"),
            LabParameter(name="Albumin", value=2.4, unit="g/dL", ref_min=3.5, ref_max=5.0, flag="L"),
            LabParameter(name="ag_ratio", value=0.7, unit=None, ref_min=1.0, ref_max=2.5, flag="L"),
        ],
    )


def main():
    # Log'daki state (görüntü zaten image_analyzer tarafından üretilmiş hali)
    base_state = {
        "message_content": "Hasta Görmede problem yaşıyor",
        "chief_complaint": None,
        "patient_age": 26,
        "patient_gender": "MALE",
        "blood_type": "A_POSITIVE",
        "chronic_diseases": [],
        "allergies": [],
        "current_medications": [],
        "lab_data": build_lab_report(),
        "image_analysis_results": {"Eye_Disease_Specialist": "Katarakt (Confidence: 88.0%)"},
    }

    print("\n" + "#" * 70)
    print("# ADIM 1 — LAB ANALYZER (Bug 2: Liver modeli atlanıyor muydu?)")
    print("#" * 70)
    lab_out = lab_analyzer_service(base_state)
    lab_results = lab_out.get("lab_analysis_results", {})
    liver_report = lab_results.get("Liver_Report", "(yok)")

    print("\n--- SONUÇ ---")
    print(f"Liver_Report           : {liver_report}")
    print(f"lab_prediction         : {lab_out.get('lab_prediction')}")
    print(f"lab_confidence         : {lab_out.get('lab_confidence')}")
    liver_ran = "Skipped" not in str(liver_report) and "Not Found" not in str(liver_report)
    print(f">>> Liver modeli ÇALIŞTI mı? : {'✅ EVET' if liver_ran else '❌ HAYIR (hâlâ atlanıyor)'}")

    # Fusion'a lab sonucunu da besle
    base_state["lab_analysis_results"] = lab_results

    print("\n" + "#" * 70)
    print("# ADIM 2 — ADAPTIVE FUSION (Bug 1: Katarakt kayboluyor + Bug 3: şikayet)")
    print("#" * 70)
    fus_out = adaptive_fusion_service(base_state)
    ctx = fus_out["fused_clinical_context"]

    print("\n--- SONUÇ ---")
    print(f"Chief_Complaint        : {ctx['Patient_Profile']['Chief_Complaint']}")
    print(f"Image_Anomalies        : {ctx['Image_Anomalies']}")
    print(f"Lab_Anomalies          : {ctx['Lab_Anomalies']}")
    print(f"Total_Anomaly_Count    : {ctx['Total_Anomaly_Count']}")

    katarakt_ok = any("Katarakt" in a for a in ctx["Image_Anomalies"])
    complaint_ok = ctx["Patient_Profile"]["Chief_Complaint"] == "Hasta Görmede problem yaşıyor"
    # Asıl hedef: raporun ham anormal değerleri (H/L) füzyona girsin (ML modelinden bağımsız)
    bilirubin_ok = any("bilirubin" in a.lower() and "HIGH" in a for a in ctx["Lab_Anomalies"])
    lab_count_ok = len(ctx["Lab_Anomalies"]) >= 8

    print("\n" + "=" * 70)
    print("ÖZET")
    print("=" * 70)
    print(f"Bug 1 — Katarakt füzyona girdi mi?               : {'✅' if katarakt_ok else '❌'}")
    print(f"Bug 2a— Liver modeli atlanmadan çalıştı mı?       : {'✅' if liver_ran else '❌'}")
    print(f"Bug 2b— Ham anormal lab değerleri yüzeye çıktı mı?: {'✅' if (bilirubin_ok and lab_count_ok) else '❌'}")
    print(f"Bug 3 — Şikayet grounded fact oldu mu?            : {'✅' if complaint_ok else '❌'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
