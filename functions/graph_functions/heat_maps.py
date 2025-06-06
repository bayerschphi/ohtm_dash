from builtins import print

import pandas as pd
import plotly.express as px

from functions.basic_functions.convert_ohtm_file import convert_ohtm_file


def heatmap_corpus(
    ohtm_file,
    option_selected: str = "all",
    show_fig: bool = True,
    return_fig: bool = False,
    z_score_global: str = "True",
    topic_filter_number: int = 0,
    topic_filter_threshold: float = 0,
    topic_filter: str = "True",
):
    ohtm_file = convert_ohtm_file(ohtm_file)

    if "z_score" in z_score_global:
        z_score = True
    else:
        z_score = False
    if "topic_filter" in z_score_global:
        topic_filter_value = True
    else:
        topic_filter_value = False
    if option_selected == "None":
        option_selected = "all"

    if ohtm_file["settings"]["topic_modeling"]["trained"] == "True":
        if option_selected == "all":
            heat_dic = {}
            for archive in ohtm_file["weight"]:
                for interview in ohtm_file["weight"][archive]:
                    heat_dic[interview] = {}
                    count = 0
                    for c in ohtm_file["weight"][archive][interview]:
                        count += 1
                        for t in ohtm_file["weight"][archive][interview][c]:
                            if t not in heat_dic[interview]:
                                heat_dic[interview].update(
                                    {t: ohtm_file["weight"][archive][interview][c][t]}
                                )
                            else:
                                heat_dic[interview].update(
                                    {
                                        t: heat_dic[interview][t]
                                        + ohtm_file["weight"][archive][interview][c][t]
                                    }
                                )
                    for entry in heat_dic[interview]:
                        heat_dic[interview].update(
                            {entry: heat_dic[interview][entry] / count}
                        )
        else:
            archive = option_selected
            heat_dic = {}
            for interview in ohtm_file["weight"][archive]:
                heat_dic[interview] = {}
                count = 0
                for c in ohtm_file["weight"][archive][interview]:
                    count += 1
                    for t in ohtm_file["weight"][archive][interview][c]:
                        if t not in heat_dic[interview]:
                            heat_dic[interview].update(
                                {t: ohtm_file["weight"][archive][interview][c][t]}
                            )
                        else:
                            heat_dic[interview].update(
                                {
                                    t: heat_dic[interview][t]
                                    + ohtm_file["weight"][archive][interview][c][t]
                                }
                            )
                for entry in heat_dic[interview]:
                    heat_dic[interview].update(
                        {entry: heat_dic[interview][entry] / count}
                    )

        if topic_filter_value:
            heat_dic_2 = {}
            for interview in heat_dic:
                if str(heat_dic[interview][str(topic_filter_number)]) >= str(
                    topic_filter_threshold
                ):
                    if "e" in str(heat_dic[interview][str(topic_filter_number)]):
                        next
                    else:
                        heat_dic_2[interview] = heat_dic[interview]
            heat_dic = heat_dic_2

        df = pd.DataFrame.from_dict(heat_dic)
        if z_score:
            mean = df.mean()
            std_dev = df.std()
            z_scores = (df - mean) / std_dev
            df = z_scores

        df = df.transpose()
        fig = px.imshow(df, color_continuous_scale="dense", aspect="auto")
        fig.update_traces(
            hovertemplate="Interview: %{y}"
            "<br>Topic: %{x}"
            "<br>Weight: %{z}<extra></extra>"
        )
        fig.update_layout(clickmode="event+select")
        fig.update_layout(clickmode="event+select")
        fig.update(layout_coloraxis_showscale=False)
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        if show_fig:
            fig.show()
        if return_fig:
            return fig

    else:
        print("No Topic Model trained")


"""
This function has to be tested in the dash. Because now it is really slow. With the chagen to possilbe different
archive namens than the first 3 letters of the interview id, i had to find another way. Maye this function has to be
improved. (17.1.2025)


"""
from dash import no_update

from functions.graph_functions.heatmap_marker import heatmap_marker_creation_normal


def heatmap_interview_simple(
    ohtm_file,
    click_data,
    click_data_2,
    ctx_triggered,
    chunk_number_storage,
    heatmap_filter: list = "",
    interview_manual_id: str = "",
):
    interview_id = None
    if click_data == "off":
        interview_id = interview_manual_id
    else:
        if interview_manual_id is not None:
            interview_id = interview_manual_id
            if interview_manual_id == "":
                interview_id = click_data["points"][0]["y"]
        else:
            if click_data is not None:
                interview_id = click_data["points"][0]["y"]
    if interview_id is not None:
        tc_indicator = False
        ohtm_file = convert_ohtm_file(ohtm_file)
        if "z_score" in heatmap_filter:
            z_score = True
        else:
            z_score = False
        if ohtm_file["settings"]["topic_modeling"]["trained"] == "True":
            dff = {}
            for archive in ohtm_file["weight"]:
                if interview_id in ohtm_file["weight"][archive]:
                    for chunks in ohtm_file["weight"][archive][interview_id]:
                        dff[chunks] = ohtm_file["weight"][archive][interview_id][chunks]

            df = pd.DataFrame.from_dict(dff)
            df.index = pd.to_numeric(df.index)

            # Berechnung der z-Standardisierung
            if z_score:
                mean = df.mean()
                std_dev = df.std()
                z_scores = (df - mean) / std_dev
                df = z_scores
                df.index = pd.to_numeric(df.index)

            fig = px.imshow(df, color_continuous_scale="dense")
            fig.update_traces(
                hovertemplate="Chunk: %{x}"
                "<br>Topic: %{y}"
                "<br>Weight: %{z}<extra></extra>"
            )
            fig.update_traces(showlegend=False)
            fig.update_traces(showscale=False)
            fig.update(layout_coloraxis_showscale=False)
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            if ctx_triggered[0]["prop_id"] == "heat_map.clickData":
                title = "Interview " + interview_id
            elif ctx_triggered[0]["prop_id"] == "interview_manual_id.value":
                title = "Interview " + interview_id
            elif ctx_triggered[0]["prop_id"] == "interview_manual_id_detail.value":
                title = "Interview " + interview_manual_id
            else:
                if "marker" in heatmap_filter:
                    marker = heatmap_marker_creation_normal(
                        click_data_2, chunk_number_storage
                    )
                    fig.add_vrect(
                        x0=marker[0],
                        x1=marker[1],
                        fillcolor="LightSalmon",
                        opacity=0.3,
                        layer="above",
                        line_width=1,
                    )
                title = "Interview " + interview_id

            df = (
                df.to_json()
            )  # dash only can store json, so this df has to be converted
            return fig, title, interview_id, chunk_number_storage, tc_indicator, df

        else:
            print("No Topic Model trained")
    else:
        return no_update, no_update, no_update, no_update, no_update, no_update
