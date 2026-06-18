def clinical_summary(patient, result):
    return f"""Clinical Summary
Patient: {patient.get('name','')} ({patient.get('code','')})
Age/Sex: {patient.get('age','')} / {patient.get('sex','')}
Diagnosis: {patient.get('diagnosis','')}
Operation: {patient.get('operation','')}

Score: {result.get('score','')}
Category: {result.get('category','')}
Result: {result.get('result','')}
Risk: {result.get('risk','')}
Interpretation: {result.get('interpretation','')}
Recommendation: {result.get('recommendation','')}
Time: {result.get('time','')}
"""
