import math
import scipy.stats as stats
import streamlit as st


# Function to compute necessary values
def compute_values(sensitivity, specificity, alpha, W, prevalence_group1, prevalence_group2):
    # Compute Z
    Z = stats.norm.ppf(1 - alpha / 2)

    # Compute M1 and M2
    M1 = ((Z ** 2 * sensitivity * (1 - sensitivity)) / W ** 2)
    print(M1)
    M2 = ((Z ** 2 * specificity * (1 - specificity)) / W ** 2)
    print(M2)

    # Compute the ideal proportion of sick people
    ideal_proportion = M1 / (M1 + M2)

    # Initialize variables
    people_from_group1 = people_from_group2 = 0

    # Check if we are within the ideal proportion range
    if prevalence_group1 <= ideal_proportion <= prevalence_group2 or prevalence_group2 <= ideal_proportion <= prevalence_group1:
        # Calculate q and split the necessary people between the two groups
        q = (prevalence_group2 - ideal_proportion) / (prevalence_group2 - prevalence_group1) if prevalence_group2 != prevalence_group1 else 0.5
        people_from_group1 = math.ceil((M1 + M2) * q)  # Apply ceiling
        people_from_group2 = math.ceil((M1 + M2) * (1 - q))  # Apply ceiling
    else:
        # The ideal proportion is not between the prevalences, so we take the group closer to the ideal_proportion
        if abs(prevalence_group1 - ideal_proportion) < abs(prevalence_group2 - ideal_proportion):
            # Group 1's prevalence is closer
            P = prevalence_group1
            people_from_group1 = math.ceil(max(M1 / P, M2 / (1 - P)))
            people_from_group2 = 0
        else:
            # Group 2's prevalence is closer
            P = prevalence_group2
            people_from_group2 = math.ceil(max(M1 / P, M2 / (1 - P)))
            people_from_group1 = 0

    # Handle cases where one of the prevalences is 0 or 1 (infinity case)
    if prevalence_group1 == 0 or prevalence_group1 == 1:
        necessary_group1 = float('inf')
    else:
        necessary_group1 = max(math.ceil(M1 / prevalence_group1), math.ceil(M2 / (1 - prevalence_group1)))

    if prevalence_group2 == 0 or prevalence_group2 == 1:
        necessary_group2 = float('inf')
    else:
        necessary_group2 = max(math.ceil(M1 / prevalence_group2), math.ceil(M2 / (1 - prevalence_group2)))

    # Special case: if one prevalence is 0 and the other is 1, gain is not calculable
    if (prevalence_group1 == 0 and prevalence_group2 == 1) or (prevalence_group1 == 1 and prevalence_group2 == 0):
        gain = "1 source is not enough"
    else:
        # Calculate gain from using both sources compared to using one source
        gain = min(necessary_group1, necessary_group2) - (people_from_group1 + people_from_group2)

    return people_from_group1, people_from_group2, gain


# Streamlit UI
st.title("Test Accuracy Calculator")

# First row: sensitivity and specificity
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

# Second row: alpha and W
col3, col4 = st.columns(2)
with col3:
    alpha = st.number_input(
        "Significance level alpha (0 to 1):",
        min_value=0.0, max_value=1.0, value=0.05, step=0.05,
        help="The significance level (alpha) is the probability of rejecting the null hypothesis when it is true. "
             "A common choice is 0.05 (5% significance level)."
    )
with col4:
    W = st.number_input(
        "W (positive value):",
        min_value=0.001, max_value=1.0, value=0.01, step=0.01,
        help="The width (W) parameter sets the tolerance for the interval of the sensitivity and specificity estimates."
    )

# Third row: prevalence_group1 and prevalence_group2
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

# Check if both prevalence values are either 0 or 1 (invalid combination)
if (prevalence_group1 == 0 and prevalence_group2 == 0) or (prevalence_group1 == 1 and prevalence_group2 == 1):
    st.error("Both prevalence values cannot be 0 or 1 at the same time. This is not valid.")
    valid_input = False

# Button to compute results, but only if inputs are valid
if st.button("Calculate") and valid_input:
    # Compute main values
    people_from_group1, people_from_group2, gain = compute_values(
        sensitivity, specificity, alpha, W, prevalence_group1, prevalence_group2
    )

    # Display main results side by side
    st.markdown("### Main Results")

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

    # Highlight the gain result without text header
    st.markdown(f"""
    <div style="background-color: #FFC107; padding: 15px; border-radius: 10px; margin-top: 20px;">
        <h2 style="text-align: center; color: #000;">Gain from using both sources: <b>{gain}</b></h2>
    </div>
    """, unsafe_allow_html=True)
