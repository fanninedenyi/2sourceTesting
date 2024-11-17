import math
import scipy.stats as stats
import streamlit as st

# Function to compute necessary values
def compute_values(sensitivity, specificity, alpha, W, prevalence_group1, prevalence_group2):
    Z = stats.norm.ppf(1 - alpha / 2)
    M1 = ((Z ** 2 * sensitivity * (1 - sensitivity)) / W ** 2)
    M2 = ((Z ** 2 * specificity * (1 - specificity)) / W ** 2)
    ideal_proportion = M1 / (M1 + M2)
    people_from_group1 = people_from_group2 = 0

    if prevalence_group1 <= ideal_proportion <= prevalence_group2 or prevalence_group2 <= ideal_proportion <= prevalence_group1:
        q = (prevalence_group2 - ideal_proportion) / (prevalence_group2 - prevalence_group1) if prevalence_group2 != prevalence_group1 else 0.5
        people_from_group1 = math.ceil((M1 + M2) * q)
        people_from_group2 = math.ceil((M1 + M2) * (1 - q))
    else:
        if abs(prevalence_group1 - ideal_proportion) < abs(prevalence_group2 - ideal_proportion):
            P = prevalence_group1
            people_from_group1 = math.ceil(max(M1 / P, M2 / (1 - P)))
        else:
            P = prevalence_group2
            people_from_group2 = math.ceil(max(M1 / P, M2 / (1 - P)))

    necessary_group1 = float('inf') if prevalence_group1 in [0, 1] else max(math.ceil(M1 / prevalence_group1), math.ceil(M2 / (1 - prevalence_group1)))
    necessary_group2 = float('inf') if prevalence_group2 in [0, 1] else max(math.ceil(M1 / prevalence_group2), math.ceil(M2 / (1 - prevalence_group2)))
    if (prevalence_group1, prevalence_group2) in [(0, 1), (1, 0)]:
        gain = "1 source is not enough"
    else:
        gain = min(necessary_group1, necessary_group2) - (people_from_group1 + people_from_group2)

    return people_from_group1, people_from_group2, gain


# Streamlit UI
st.title("Test Accuracy Calculator")

# Choice between modes
mode = st.radio("Select input mode:", options=["Interval", "Threshold"])

if mode == "Interval":  # Interval mode
    st.subheader("Interval Mode")
    col1, col2 = st.columns(2)
    with col1:
        sensitivity = st.number_input("Sensitivity (0 to 1):", 0.0, 1.0, 0.99, 0.01)
    with col2:
        specificity = st.number_input("Specificity (0 to 1):", 0.0, 1.0, 0.99, 0.01)
    W = st.number_input("W (positive value):", 0.001, 1.0, 0.01, 0.01)
else:  # Threshold mode
    st.subheader("Threshold Mode")
    col1, col2 = st.columns(2)
    with col1:
        sensitivity_threshold = st.number_input("Sensitivity Threshold (0 to 1):", 0.0, 1.0, 0.9, 0.01)
    with col2:
        specificity_threshold = st.number_input("Specificity Threshold (0 to 1):", 0.0, 1.0, 0.9, 0.01)

    # Convert thresholds to sensitivity, specificity, and width
    sensitivity = (sensitivity_threshold + 1) / 2
    specificity = (specificity_threshold + 1) / 2
    W = (1 - sensitivity_threshold) / 2

alpha = st.number_input("Significance level alpha (0 to 1):", 0.0, 1.0, 0.05, 0.05)

col3, col4 = st.columns(2)
with col3:
    prevalence_group1 = st.number_input("Prevalence in group 1 (0 to 1):", 0.0, 1.0, 0.1, 0.05)
with col4:
    prevalence_group2 = st.number_input("Prevalence in group 2 (0 to 1):", 0.0, 1.0, 0.65, 0.05)

if st.button("Calculate"):
    people_from_group1, people_from_group2, gain = compute_values(
        sensitivity, specificity, alpha, W, prevalence_group1, prevalence_group2
    )

    col5, col6 = st.columns(2)
    with col5:
        st.metric("People from Group 1", people_from_group1)
    with col6:
        st.metric("People from Group 2", people_from_group2)
    st.success(f"Gain from using both sources: {gain}")
