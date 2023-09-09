"""Running Coach"""

import os

import pandas as pd
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

st.set_page_config(page_title="Running", page_icon="🏃")
st.sidebar.header("Running")
st.sidebar.write(
    """
One run can change your day, many runs can change your life.
"""
)

st.header("Running Coach 🏃", divider=True)
target_column, dashboard_column, recommendation_column = st.columns(3)


@st.cache_data
def load_records(file):
    """Load records data"""
    records_data = pd.read_csv(file)
    return records_data


@st.cache_data
def load_workouts(file):
    """Load workouts data"""
    workouts_data = pd.read_csv(file)
    return workouts_data


@st.cache_data
def get_records_for_workout(
    all_records, record_type, workout_startdate, workout_enddate
):
    """Get details of a record type for a workout"""
    records = all_records.loc[all_records["type"] == record_type]
    records = records.loc[
        (records["startDate"] >= workout_startdate)
        & (records["endDate"] <= workout_enddate)
    ]
    unit = records["unit"].iloc[0]
    if record_type in [
        "HeartRate",
        "RunningStrideLength",
        "RunningPower",
        "RunningVerticalOscillation",
        "RunningGroundContactTime",
        "RunningSpeed",
    ]:
        return {
            f"max {record_type} ({unit})": records["value"].max(),
            f"min {record_type} ({unit})": records["value"].min(),
            f"mean {record_type} ({unit})": records["value"].mean(),
        }
    if record_type in ["ActiveEnergyBurned", "BasalEnergyBurned"]:
        return {f"{record_type} ({unit})": records["value"].sum()}
    return {}


@st.cache_data
def get_workout_statistics(all_workouts, workout_type, all_records, record_types):
    """Get workout statisticas"""
    workouts = all_workouts.loc[all_workouts["workoutActivityType"] == workout_type]
    statistics = []
    for index, row in workouts.iterrows():
        statistic = {}
        statistic["type"] = workout_type
        statistic[f'duration ({row["durationUnit"]})'] = row["duration"]
        statistic["time"] = row["startDate"]
        statistic["date"] = row["startDate"][5:10]
        for record_type in record_types:
            statistic.update(
                get_records_for_workout(
                    all_records, record_type, row["startDate"], row["endDate"]
                )
            )
            if record_type == "RunningSpeed":
                pace = 1000 / 60 / statistic["mean RunningSpeed (m/s)"]
                statistic["pace (min/km)"] = f"{pace:.2f}"
                statistic[
                    "distance (km)"
                ] = f'{(statistic["duration (min)"] / pace):.2f}'
        statistics.append(statistic)
    return statistics


def show_status(reach_target):
    """Show if target is reached"""
    if reach_target:
        return st.success("You have reached the target!", icon="✅")
    return st.error("You are doing fine... Just keep running!", icon="⛔")


with target_column:
    st.subheader("Target")
    st.write(
        f"""
        Pace: {os.getenv('PACE_TARGET')} min/km\n
        Heart Rate: {os.getenv('HEART_RATE_TARGET')} count/min\n
        Stride Length: {os.getenv('STRIDE_LENGTH_TARGET')} m
        """
    )

    st.divider()
    records = load_records(os.getenv("HEALTH_RECORD_FILE"))
    workouts = load_workouts(os.getenv("HEALTH_WORKOUT_FILE"))
    runnings = get_workout_statistics(
        workouts,
        "Running",
        records,
        [
            "HeartRate",
            "RunningStrideLength",
            "RunningPower",
            "RunningVerticalOscillation",
            "RunningGroundContactTime",
            "RunningSpeed",
            "ActiveEnergyBurned",
            "BasalEnergyBurned",
        ],
    )

    runnings_pd = pd.DataFrame(runnings)
    runnings_pd["distance (km)"] = runnings_pd["distance (km)"].astype("float")
    runnings_pd["pace (min/km)"] = runnings_pd["pace (min/km)"].astype("float")

    running_dates = [x["time"] for x in runnings]
    default_msg = "Overview"
    running_dates.insert(0, default_msg)

    running_date = st.selectbox("Running history", running_dates)
    if running_date != default_msg:
        running_statistics = [x for x in runnings if x["time"] == running_date][0]

        running_statistics_pd = pd.DataFrame(running_statistics, index=[0])
        running_statistics_pd["distance (km)"] = running_statistics_pd[
            "distance (km)"
        ].astype("float")
        running_statistics_pd["pace (min/km)"] = running_statistics_pd[
            "pace (min/km)"
        ].astype("float")

    ask_coach = st.button(
        "Ask coach", type="primary", disabled=(running_date == default_msg)
    )

    st.divider()
    if st.toggle("Show raw data"):
        if running_date != default_msg:
            st.caption("running statistics")
            st.write(running_statistics)
        else:
            st.caption("workout data")
            st.write(workouts)
            st.caption("record data")
            st.write(records)

with dashboard_column:
    st.subheader("Dashboard")
    analysis = st.empty()
    if running_date == default_msg:
        with analysis.container():
            overall = runnings_pd[["date", "distance (km)", "duration (min)"]]
            st.pyplot(
                overall.plot(title="Distance and Duration", x="date", kind="bar").figure
            )
            st.pyplot(
                runnings_pd.plot(
                    title="Pace", x="date", y="pace (min/km)", kind="scatter"
                )
                .axhline(y=int(os.getenv("PACE_TARGET")), color="red")
                .figure
            )
            st.pyplot(
                runnings_pd.plot(
                    title="Heart Rate",
                    x="date",
                    y="mean HeartRate (count/min)",
                    kind="scatter",
                )
                .axhline(y=int(os.getenv("HEART_RATE_TARGET")), color="red")
                .figure
            )
            st.pyplot(
                runnings_pd.plot(
                    title="Stride Length",
                    x="date",
                    y="mean RunningStrideLength (m)",
                    kind="scatter",
                )
                .axhline(y=float(os.getenv("STRIDE_LENGTH_TARGET")), color="red")
                .figure
            )
    else:
        analysis.empty()
        show_status(
            float(running_statistics["pace (min/km)"]) < float(os.getenv("PACE_TARGET"))
        )
        st.pyplot(
            running_statistics_pd.plot(
                title="Pace", x="date", y="pace (min/km)", kind="scatter"
            )
            .axhline(y=int(os.getenv("PACE_TARGET")), color="red")
            .figure
        )
        show_status(
            float(running_statistics["mean HeartRate (count/min)"])
            < float(os.getenv("HEART_RATE_TARGET"))
        )
        st.pyplot(
            running_statistics_pd.plot(
                title="Heart Rate",
                x="date",
                y="mean HeartRate (count/min)",
                kind="scatter",
            )
            .axhline(y=int(os.getenv("HEART_RATE_TARGET")), color="red")
            .figure
        )
        show_status(
            float(running_statistics["mean RunningStrideLength (m)"])
            > float(os.getenv("HEART_RATE_TARGET"))
        )
        st.pyplot(
            running_statistics_pd.plot(
                title="Stride Length",
                x="date",
                y="mean RunningStrideLength (m)",
                kind="scatter",
            )
            .axhline(y=float(os.getenv("STRIDE_LENGTH_TARGET")), color="red")
            .figure
        )

with recommendation_column:
    st.subheader("Recommendation")
    coach_says = st.empty()
    if ask_coach:
        coach_says.empty()
        SYSTEM_MESSAGE = """
            You are a very professional running coach with a passion for helping your coachee to achieve his or her goal. 
            You have a deep understanding of running performance metrics. Your task is to summarize the running data and show
            them to the coachee, then provide recommendations to help the coachee to improve his or her running performance in 
            a data driven method.
            """

        HUMAN_MESSAGE = f"""
            I am a {os.getenv('AGE')} years old {os.getenv('GENDER')}. I am {os.getenv('HEIGHT')} cm tall 
            and weigh {os.getenv('WEIGHT')} kg. When I run, my target is to keep heart rate less than {os.getenv('HEART_RATE_TARGET')} 
            count/min, stride length greater than {os.getenv('STRIDE_LENGTH_TARGET')} m, and running pace less than {os.getenv('PACE_TARGET')} min/km.
            Here is my running data in json format:\n {running_statistics}\n Please analyze and make recommendations based on the running data and 
            my age, gender, weight and height. Optionally please provide links to some learning resources. The response should be in bullet format.
            """

        st_callback = StreamlitCallbackHandler(coach_says)

        chat = ChatOpenAI(
            streaming=True,
            callbacks=[st_callback],
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        recommendation = chat(
            [
                SystemMessage(content=SYSTEM_MESSAGE),
                HumanMessage(content=HUMAN_MESSAGE),
            ]
        )

        coach_says.empty().write(recommendation.content)
