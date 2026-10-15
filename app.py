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

                # Try the primary model, then a supported fallback if the
                # primary model is temporarily unavailable.
                response = None
                models_to_try = [
                    "gemini-3.8-flash",
                    "gemini-3.5-flash-lite",
                ]
                last_error = None

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[prompt, image_part]
                        )
                        if response.text:
                            break
                        last_error = RuntimeError(
                            f"{model_name} returned an empty response."
                        )
                    except Exception as model_error:
                        last_error = model_error
                        error_text = str(model_error).upper()
                        status_code = getattr(model_error, "code", None)

                        # Only switch models for temporary availability errors.
                        if status_code == 503 or "503" in error_text or "UNAVAILABLE" in error_text:
                            continue
                        raise

                if response is None or not response.text:
                    if last_error:
                        raise last_error
                    raise RuntimeError("No Gemini model returned a response.")

            if response.text:
                st.session_state["recovery_result"] = response.text
                st.session_state["last_item_name"] = uploaded.name
            else:
                st.error(
                    "The AI returned no text. Please try another photo."
                )

        except Exception as e:
            error_text = str(e).upper()
            status_code = getattr(e, "code", None)

            if status_code == 503 or "503" in error_text or "UNAVAILABLE" in error_text:
                st.warning(
                    "Gemini is temporarily busy, and the backup model is "
                    "also unavailable. Please wait a few minutes and try again. "
                    "Your uploaded image is still available."
                )
            elif status_code == 429 or "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                st.warning(
                    "The Gemini API usage limit has been reached. "
                    "Please check your API quota or try again after it resets."
                )
            elif status_code in (401, 403) or "API KEY" in error_text or "PERMISSION_DENIED" in error_text:
                st.error(
                    "Gemini API access was denied. Check that your API key "
                    "is valid and that the selected models are available to your project."
                )
            else:
                st.error("AI analysis failed. Please try again.")
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
