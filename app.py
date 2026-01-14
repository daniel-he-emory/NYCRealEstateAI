"""
NYC Real Estate AI - Streamlit Demo App

A simple property search and analysis interface.
"""

import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()


# Page config
st.set_page_config(
    page_title="NYC Real Estate AI",
    page_icon="🏙️",
    layout="wide"
)

# Title
st.title("🏙️ NYC Real Estate AI")
st.markdown("*Find your perfect NYC property with intelligent analysis*")
st.divider()


# Sidebar filters
st.sidebar.header("🔍 Search Filters")

# Load neighborhoods
@st.cache_data(ttl=600)
def load_neighborhoods():
    try:
        result = supabase.table('neighborhoods').select('neighborhood_name, borough').order('neighborhood_name').execute()
        return result.data
    except Exception as e:
        st.error(f"Error loading neighborhoods: {e}")
        return []

neighborhoods_data = load_neighborhoods()
neighborhood_names = ['All'] + [n['neighborhood_name'] for n in neighborhoods_data]

# Filters
selected_neighborhood = st.sidebar.selectbox("Neighborhood", neighborhood_names)

col1, col2 = st.sidebar.columns(2)
with col1:
    min_price = st.number_input("Min Price ($)", min_value=0, value=500000, step=50000)
with col2:
    max_price = st.number_input("Max Price ($)", min_value=0, value=3000000, step=50000)

col1, col2 = st.sidebar.columns(2)
with col1:
    min_beds = st.selectbox("Min Bedrooms", [0, 1, 2, 3, 4, 5], index=0)
with col2:
    max_beds = st.selectbox("Max Bedrooms", [1, 2, 3, 4, 5, 6], index=5)

# Amenities
st.sidebar.subheader("Amenities")
col1, col2 = st.sidebar.columns(2)
with col1:
    has_elevator = st.checkbox("Elevator")
    has_doorman = st.checkbox("Doorman")
with col2:
    has_gym = st.checkbox("Gym")
    has_parking = st.checkbox("Parking")

pet_friendly = st.sidebar.checkbox("Pet Friendly")

# Status filter
status_filter = st.sidebar.multiselect(
    "Status",
    ["Active", "Price Change", "In Contract"],
    default=["Active", "Price Change"]
)

st.sidebar.divider()
show_investment = st.sidebar.checkbox("Show Investment Metrics", value=True)
show_distress = st.sidebar.checkbox("Highlight Distressed Properties", value=True)


# Load properties function
@st.cache_data(ttl=60)
def load_properties(neighborhood, min_p, max_p, min_b, max_b, statuses, elevator, doorman, gym, parking, pets):
    try:
        # Build query
        query = supabase.table('properties').select(
            '*, neighborhoods(neighborhood_name, borough, median_price_per_sqft, rent_to_price_ratio)'
        )

        # Apply filters - we'll do most filtering client-side for simplicity
        result = query.execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)

        # Client-side filtering
        if neighborhood != 'All':
            df = df[df['neighborhoods'].apply(lambda x: x['neighborhood_name'] == neighborhood if x else False)]

        df = df[
            (df['current_price'] >= min_p) &
            (df['current_price'] <= max_p) &
            (df['bedrooms'] >= min_b) &
            (df['bedrooms'] <= max_b) &
            (df['status'].isin(statuses))
        ]

        if elevator:
            df = df[df['has_elevator'] == True]
        if doorman:
            df = df[df['has_doorman'] == True]
        if gym:
            df = df[df['has_gym'] == True]
        if parking:
            df = df[df['has_parking'] == True]
        if pets:
            df = df[df['pet_friendly'] == True]

        return df

    except Exception as e:
        st.error(f"Error loading properties: {e}")
        return pd.DataFrame()


# Load data
with st.spinner("Loading properties..."):
    df = load_properties(
        selected_neighborhood,
        min_price,
        max_price,
        min_beds,
        max_beds,
        status_filter,
        has_elevator,
        has_doorman,
        has_gym,
        has_parking,
        pet_friendly
    )

# Display results
st.header(f"📊 Found {len(df)} Properties")

if len(df) == 0:
    st.warning("No properties match your criteria. Try adjusting the filters.")
else:
    # Sort options
    sort_by = st.selectbox(
        "Sort by:",
        ["Price (Low to High)", "Price (High to Low)", "Price per SQFT", "Cap Rate (Highest)", "Days on Market"]
    )

    if sort_by == "Price (Low to High)":
        df = df.sort_values('current_price', ascending=True)
    elif sort_by == "Price (High to Low)":
        df = df.sort_values('current_price', ascending=False)
    elif sort_by == "Price per SQFT":
        df = df.sort_values('price_per_sqft', ascending=True)
    elif sort_by == "Cap Rate (Highest)":
        df = df.sort_values('cap_rate', ascending=False)
    elif sort_by == "Days on Market":
        df = df.sort_values('days_on_market', ascending=False)

    # Display properties
    for idx, row in df.iterrows():
        with st.container():
            # Header with price and distress flag
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                neighborhood_name = row['neighborhoods']['neighborhood_name'] if row['neighborhoods'] else "Unknown"
                borough = row['neighborhoods']['borough'] if row['neighborhoods'] else ""
                st.subheader(f"{row['bedrooms']}BR / {row['bathrooms']}BA in {neighborhood_name}, {borough}")

            with col2:
                st.metric("Price", f"${row['current_price']:,.0f}")

            with col3:
                if show_distress and row.get('distress_flag'):
                    if row['distress_flag'] == 'High':
                        st.error(f"🔥 {row['distress_flag']} Distress")
                    elif row['distress_flag'] == 'Medium':
                        st.warning(f"⚠️ {row['distress_flag']} Distress")
                    else:
                        st.success(f"✅ {row['distress_flag']} Distress")

            # Details
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("SQFT", f"{row['sqft']:,}" if row['sqft'] else "N/A")
            with col2:
                ppsf = row.get('price_per_sqft', 0)
                st.metric("$/SQFT", f"${ppsf:,.0f}" if ppsf else "N/A")
            with col3:
                st.metric("HOA/Month", f"${row['monthly_hoa']:,.0f}" if row['monthly_hoa'] else "N/A")
            with col4:
                st.metric("Days on Market", f"{row['days_on_market']}")
            with col5:
                status_emoji = "🟢" if row['status'] == 'Active' else "🟡" if row['status'] == 'Price Change' else "🔵"
                st.metric("Status", f"{status_emoji} {row['status']}")

            # Investment metrics (if enabled)
            if show_investment and row.get('cap_rate'):
                st.markdown("**📈 Investment Metrics**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    cap_rate = row.get('cap_rate', 0)
                    cap_color = "green" if cap_rate >= 4 else "orange" if cap_rate >= 3 else "red"
                    st.markdown(f"**Cap Rate:** :{cap_color}[{cap_rate:.2f}%]")

                with col2:
                    grm = row.get('gross_rent_multiplier', 0)
                    grm_color = "green" if grm > 0 and grm <= 15 else "orange" if grm <= 20 else "red"
                    st.markdown(f"**GRM:** :{grm_color}[{grm:.1f}x]")

                with col3:
                    rent = row.get('estimated_monthly_rent', 0)
                    st.markdown(f"**Est. Rent:** ${rent:,.0f}/mo")

                with col4:
                    rent_ratio = row.get('rent_to_price_ratio', 0)
                    st.markdown(f"**Rent/Price:** {rent_ratio:.2f}%")

            # Amenities
            amenities = []
            if row.get('has_elevator'): amenities.append("🛗 Elevator")
            if row.get('has_doorman'): amenities.append("🚪 Doorman")
            if row.get('has_gym'): amenities.append("💪 Gym")
            if row.get('has_parking'): amenities.append("🅿️ Parking")
            if row.get('has_roof_deck'): amenities.append("🏞️ Roof Deck")
            if row.get('pet_friendly'): amenities.append("🐕 Pet Friendly")

            if amenities:
                st.markdown("**Amenities:** " + " • ".join(amenities))

            # Description (truncated)
            if row.get('property_description'):
                with st.expander("📄 View Description"):
                    st.write(row['property_description'])
                    st.markdown(f"**Address:** {row['address']}")
                    st.markdown(f"**Floor:** {row.get('floor_level', 'N/A')} (Floor #{row.get('floor_number', 'N/A')})")
                    st.markdown(f"**Exposure:** {row.get('exposure', 'N/A')}")
                    st.markdown(f"**Year Built:** {row.get('year_built', 'N/A')}")
                    st.markdown(f"**Subway:** {row.get('subway_distance', 'N/A')} min walk to {row.get('nearest_subway_lines', 'N/A')}")

                    if row.get('listing_url'):
                        st.markdown(f"[View Original Listing]({row['listing_url']})")

            # Price history
            if row.get('price_history'):
                try:
                    price_history = json.loads(row['price_history']) if isinstance(row['price_history'], str) else row['price_history']
                    if len(price_history) > 1:
                        with st.expander("📉 Price History"):
                            history_df = pd.DataFrame(price_history)
                            history_df['date'] = pd.to_datetime(history_df['date'])
                            history_df = history_df.sort_values('date')

                            st.line_chart(history_df.set_index('date')['price'])

                            total_cut = row.get('total_cut_percent', 0)
                            if total_cut > 0:
                                st.markdown(f"**Total Price Reduction:** {total_cut:.1f}% (${row['original_price'] - row['current_price']:,.0f})")
                except:
                    pass

            st.divider()

# Footer stats
if len(df) > 0:
    st.header("📊 Market Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_price = df['current_price'].mean()
        st.metric("Average Price", f"${avg_price:,.0f}")

    with col2:
        avg_ppsf = df['price_per_sqft'].mean()
        st.metric("Avg Price/SQFT", f"${avg_ppsf:,.0f}")

    with col3:
        avg_dom = df['days_on_market'].mean()
        st.metric("Avg Days on Market", f"{avg_dom:.0f}")

    with col4:
        if show_investment:
            avg_cap = df[df['cap_rate'] > 0]['cap_rate'].mean()
            st.metric("Avg Cap Rate", f"{avg_cap:.2f}%")
        else:
            median_price = df['current_price'].median()
            st.metric("Median Price", f"${median_price:,.0f}")
