import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="NUERABIN Rescue",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071b17, #10352a);
    color: #f2fff6;
}
h1, h2, h3, p, label {
    color: #f2fff6;
}
div[data-testid="stMetric"] {
    background: #174335;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("NUERABIN RESCUE")
st.subheader("AI-powered waste recovery")
st.write(
    "Upload an image. Let AI identify the item and explore "
    "ways to reuse, repair, donate, recycle, compost or dispose of it safely."
)

# Read the API key from Streamlit's private secrets configuration
api_key = st.secrets["GEMINI_API_KEY"]

uploaded = st.file_uploader(
    "Upload a photo of any item",
    type=["jpg", "jpeg", "png", "webp"]
)

extra_info = st.text_input(
    "Anything else about the item? (optional)",
    placeholder="e.g. It no longer works, or it is slightly damaged"
)

if uploaded:
    st.image(
        uploaded,
        caption="Uploaded item",
        use_container_width=True
    )

    if st.button("Analyze with AI", type="primary"):
        prompt = """
You are NUERABIN Rescue, an assistant for responsible waste recovery.

Examine the uploaded image and respond in clear, practical English.

Identify:
1. The most likely object and visible material.
2. Any visible condition or damage. Do not guess hidden details.
3. The best next step, prioritizing reuse, repair, donation,
   recycling or composting when appropriate.
4. Safe preparation and handling instructions.
5. The appropriate disposal or collection destination.
6. One alternative recovery option.
7. Any uncertainty or safety concern.

If the image does not show an identifiable item, say so and ask
for a clearer photo. Do not invent a specific object.

For electronics, batteries, chemicals, medical waste or other
potentially hazardous items, recommend suitable authorized
collection or professional guidance. Do not recommend ordinary
bin disposal for hazardous items.

Do not claim that a local facility exists unless verified.
Explain that local acceptance rules may differ.

Use these headings:
### Item identified
### Recommended recovery action
### How to prepare it
### Where it should go
### Alternative option
### Safety and uncertainty

Be honest about uncertainty. Do not claim that the image analysis
is always correct.
"""

        if extra_info.strip():
            prompt += "\nAdditional user information: " + extra_info.strip()

        try:
            with st.spinner("AI is examining your item..."):
                client = genai.Client(api_key=api_key)

                image_part = types.Part.from_bytes(
                    data=uploaded.getvalue(),
                    mime_type=uploaded.type
                )

                response = client.models.generate_content(
                    model="	gemini-4-argon",
                    contents=[prompt, image_part]
                )

            if response.text:
                st.session_state["recovery_result"] = response.text
                st.session_state["last_item_name"] = uploaded.name
            else:
                st.error(
                    "The AI returned no text. Please try another photo."
                )

        except Exception as e:
            st.error(
                "AI analysis failed. Check your internet connection, "
                "API access and usage limits."
            )
            st.caption(f"Technical details: {e}")

if st.session_state.get("recovery_result"):
    st.divider()
    st.header("Your AI recovery plan")
    st.markdown(st.session_state["recovery_result"])

    st.info(
        "AI recommendations are suggestions. Verify the material, "
        "safety requirements and local waste collection rules."
    )

st.divider()
st.header("Our mission")
st.write(
    "NUERABIN goes beyond sorting waste. It helps people discover "
    "what an item is, how it might be recovered, and what action "
    "to take next."
)
st.caption("Hackathon prototype | AI-generated guidance")

