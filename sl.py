import math
import scipy.stats as stats
import streamlit as st

# Function to compute necessary values
def compute_values(sensitivity, specificity, alpha, W_sens, W_spec, prevalence_group1, prevalence_group2):
    Z = stats.norm.ppf(1 - alpha / 2)
    M1 = ((Z ** 2 * sensitivity * (1 - sensitivity)) / W_sens ** 2)
    M2 = ((Z ** 2 * specificity * (1 - specificity)) / W_spec ** 2)
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
    st.help("In this mode, you enter a range (width) for sensitivity and specificity, which helps calculate the necessary number of individuals for each group.")
    
    col1, col2 = st.columns(2)
    with col1:
        sensitivity = st.number_input(
            "Sensitivity (0 to 1):",
            min_value=0.0, max_value=1.0, value=0.99, step=0.01,
            help="Sensitivity refers to the probability that a diagnostic tool correctly identifies a sick individual as sick."
        )
    with col2:
        specificity = st.number_input(
            "Specificity (0 to 1):",
            min_value=0.0, max_value=1.0, value=0.99, step=0.01,
            help="Specificity refers to the probability that a diagnostic tool correctly identifies a healthy individual as healthy."
        )

    col3, col4 = st.columns(2)
    with col3:
        alpha = st.number_input(
            "Significance level alpha (0 to 1):",
            min_value=0.0, max_value=1.0, value=0.05, step=0.05,
            help="The significance level (alpha) is the probability of rejecting the null hypothesis when it is true. "
                 "A common choice is 0.05 (5% significance level)."
        )

    # Option to choose different widths for sensitivity and specificity
    use_different_widths = st.checkbox("Use different width values for Sensitivity and Specificity?")
    
    if use_different_widths:
        col5, col6 = st.columns(2)
        with col5:
            W_sens = st.number_input(
                "Width for Sensitivity (W_sens, positive value):",
                min_value=0.001, max_value=1.0, value=0.01, step=0.01,
                help="The width parameter for sensitivity sets the tolerance for its interval estimate."
            )
        with col6:
            W_spec = st.number_input(
                "Width for Specificity (W_spec, positive value):",
                min_value=0.001, max_value=1.0, value=0.01, step=0.01,
                help="The width parameter for specificity sets the tolerance for its interval estimate."
            )
    else:
        W = st.number_input(
            "Width (W, positive value):",
            min_value=0.001, max_value=1.0, value=0.01, step=0.01,
            help="The width (W) parameter sets the tolerance for both sensitivity and specificity estimates."
        )
        W_sens = W
        W_spec = W

else:  # Threshold mode
    st.subheader("Threshold Mode")
    st.help("In this mode, you set a threshold for sensitivity and specificity. These thresholds are used to calculate the necessary sample sizes.")

    col1, col2 = st.columns(2)
    with col1:
        sensitivity_threshold = st.number_input(
            "Sensitivity Threshold (0 to 1):",
            min_value=0.0, max_value=1.0, value=0.98, step=0.01,
            help="Minimum threshold for sensitivity."
        )
    with col2:
        specificity_threshold = st.number_input(
            "Specificity Threshold (0 to 1):",
            min_value=0.0, max_value=1.0, value=0.98, step=0.01,
            help="Minimum threshold for specificity."
        )

    alpha = st.number_input(
        "Significance level alpha (0 to 1):",
        min_value=0.0, max_value=1.0, value=0.05, step=0.05,
        help="The significance level (alpha) is the probability of rejecting the null hypothesis when it is true. "
             "A common choice is 0.05 (5% significance level)."
    )

    # Convert thresholds to sensitivity, specificity, and width
    sensitivity = (sensitivity_threshold + 1)/2
    specificity = (specificity_threshold +1)/2
    W_sens = (1 - sensitivity_threshold) / 2  # Adjusted to align with threshold logic
    W_spec = (1 - specificity_threshold) / 2  # Adjusted to align with threshold logic

col5, col6 = st.columns(2)
with col5:
    prevalence_group1 = st.number_input(
        "Prevalence in group 1 (0 to 1):",
        min_value=0.0, max_value=1.0, value=0.1, step=0.05,
        help="Prevalence is the proportion of sick individuals in the first population."
    )
with col6:
    prevalence_group2 = st.number_input(
        "Prevalence in group 2 (0 to 1):",
        min_value=0.0, max_value=1.0, value=0.65, step=0.05,
        help="Prevalence is the proportion of sick individuals in the second population."
    )

# Validate input based on the combination of both prevalences
valid_input = True

if (prevalence_group1 == 0 and prevalence_group2 == 0) or (prevalence_group1 == 1 and prevalence_group2 == 1):
    st.error("Both prevalence values cannot be 0 or 1 at the same time. This is not valid.")
    valid_input = False

if st.button("Calculate") and valid_input:
    people_from_group1, people_from_group2, gain = compute_values(
        sensitivity, specificity, alpha, W_sens, W_spec, prevalence_group1, prevalence_group2
    )

    col7, col8 = st.columns(2)
    with col7:
        st.markdown(f"""
        <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 10px;">
            <h3 style="text-align: center; color: #4CAF50;">People from Group 1</h3>
            <h1 style="text-align: center;">{people_from_group1}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
        <div style="border: 2px solid #2196F3; padding: 10px; border-radius: 10px;">
            <h3 style="text-align: center; color: #2196F3;">People from Group 2</h3>
            <h1 style="text-align: center;">{people_from_group2}</h1>
        </div>
        """, unsafe_allow_html=True)

    # Display Estimated Gain
    st.markdown(f"""
    <div style="border: 2px solid #FFC107; padding: 10px; border-radius: 10px;">
        <h3 style="text-align: center; color: #FFC107;">Estimated Gain</h3>
        <h2 style="text-align: center;">{gain} individuals</h2>
    </div>
    """, unsafe_allow_html=True)
