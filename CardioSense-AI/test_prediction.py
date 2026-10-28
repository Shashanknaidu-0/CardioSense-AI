from app.predictor import CardioSensePredictor


print("=" * 60)
print("CARDIOSENSE AI — MODEL LOADING TEST")
print("=" * 60)

predictor = CardioSensePredictor()

print("\n[OK] All models loaded successfully!")


patient = {
    "age": 55,
    "gender": 1.0,
    "bmi": 28.5,
    "waist_circumference": 95.0,
    "sys_bp": 135,
    "dia_bp": 85,
    "pulse_rate": 72,
    "tot_chol": 210.0,
    "hdl_chol": 45.0,
    "hba1c": 5.8,
    "hs_crp": 3.5
}


result = predictor.predict(patient)


print("\nCVD Risk:")
print(
    f"{result['risk_percent']:.2f}%"
)

print("\nIndividual Model Predictions:")

for model, probability in result["models"].items():

    print(
        f"{model:25s}: "
        f"{probability * 100:.2f}%"
    )


print("\nThreshold Decisions:")

for mode, decision in result["decisions"].items():

    print(
        f"{mode:20s}: "
        f"{'POSITIVE' if decision else 'NEGATIVE'}"
    )


print("\n" + "=" * 60)
print("PREDICTION ENGINE TEST COMPLETE")
print("=" * 60)