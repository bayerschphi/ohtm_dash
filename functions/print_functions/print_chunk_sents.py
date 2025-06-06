"""
This function prints alle the sents, that are in one chunk, including the speakers.
"""

import pandas as pd
from dash import ctx, html
from functions.basic_functions.create_link_to_ohd import create_link


def chunk_sent_drawing(
    ohtm_file, click_data_input, chunk_number, interview_id, chronology_df, tc_indicator, show_links: bool = True
):
    anonymized_status = False
    if ctx.triggered[0]["prop_id"] == "+_button_frontpage.n_clicks":
        chunk_id = int(chunk_number) + 1
    elif ctx.triggered[0]["prop_id"] == "+_button_detail.n_clicks":
        chunk_id = int(chunk_number) + 1
    elif ctx.triggered[0]["prop_id"] == "-_button_frontpage.n_clicks":
        chunk_id = int(chunk_number) - 1
    elif ctx.triggered[0]["prop_id"] == "-_button_detail.n_clicks":
        chunk_id = int(chunk_number) - 1
    else:
        if tc_indicator:
            chronology_df = pd.read_json(chronology_df, orient="records")
            time_id = click_data_input["points"][0]["x"]
            try:
                row_index = chronology_df.index.get_loc(
                    chronology_df[chronology_df["minute"] == time_id].index[0]
                )
            except IndexError:
                # If due to rownding errors, the value is not found, we search for the next value near to the one.
                closest_match = chronology_df.iloc[
                    (chronology_df["minute"] - time_id).abs().argmin()
                ].name
                row_index = chronology_df.index.get_loc(closest_match)

            # die Information aus dem DF aus Chronology. Hier wird die Zeit und das zugehörige
            # DF gespeichert. Wir müssen zunächst den Index der Zeitangabe finden
            chunk_id = chronology_df.loc[row_index]["ind"]
            # mit dem Index der Zeitangabe kann hier der Chunkwert ausgelesen werden und als chunk_id übergeben werden
        else:
            chunk_id = click_data_input["points"][0]["x"]

    sent_example = []
    speaker = "None"
    chunk_start_marker = 0
    link_tape = "1"
    for archive in ohtm_file["corpus"]:
        if interview_id in ohtm_file["corpus"][archive]:
            try:
                if ohtm_file["corpus"][archive][interview_id]["anonymized"] == "True":
                    anonymized_status = True
            except KeyError:
                anonymized_status = False
            for sentence_number in ohtm_file["corpus"][archive][interview_id]["sent"]:
                if ohtm_file["corpus"][archive][interview_id]["sent"][sentence_number][
                    "chunk"
                ] == int(chunk_id):
                    chunk_start_marker += 1
                    if chunk_start_marker == 1:  # to mark the beginning of the chunk for the first timecode
                        if ohtm_file["corpus"][archive][interview_id]["sent"][sentence_number]["time"] != {}:
                            timcodes_available = True
                            chunk_start_time = ohtm_file["corpus"][archive][interview_id]["sent"][sentence_number][
                                "time"]
                            link_tape = ohtm_file["corpus"][archive][interview_id]["sent"][sentence_number]["tape"]
                        else:
                            timcodes_available = False
                    if (
                        ohtm_file["corpus"][archive][interview_id]["sent"][
                            sentence_number
                        ]["speaker"]
                        == {}
                    ):
                        sent_example.append(
                            ohtm_file["corpus"][archive][interview_id]["sent"][
                                sentence_number
                            ]["raw"]
                            + " "
                        )
                    else:
                        if (
                            speaker
                            == ohtm_file["corpus"][archive][interview_id]["sent"][
                                sentence_number
                            ]["speaker"]
                        ):
                            sent_example.append(
                                ohtm_file["corpus"][archive][interview_id]["sent"][
                                    sentence_number
                                ]["raw"]
                                + ". "
                            )
                        else:
                            sent_example.append(
                                "\n"
                                + "*"
                                + ohtm_file["corpus"][archive][interview_id]["sent"][
                                    sentence_number
                                ]["speaker"]
                                + "*: "
                            )
                            sent_example.append(
                                ohtm_file["corpus"][archive][interview_id]["sent"][
                                    sentence_number
                                ]["raw"]
                                + ". "
                            )
                            speaker = ohtm_file["corpus"][archive][interview_id][
                                "sent"
                            ][sentence_number]["speaker"]
                            if ohtm_file["corpus"][archive][interview_id]["sent"][sentence_number]["time"] != {}:
                                chunk_end_time = \
                                    ohtm_file["corpus"][archive][interview_id]["sent"][sentence_number]["time"]
            if timcodes_available:
                sent_example.append("\n" + "\n" + "Timecode: " + str(chunk_start_time) + "–" + str(chunk_end_time))
            else:
                chunk_start_time = "False"
                link_tape = "1"
            if anonymized_status:
                link = create_link(archive.lower(), interview_id.lower(), chunk_start_time, link_tape)
                sent_example = ("This interview is anonymized and can be found here: " + "\n", html.A(link, href=link, target="_blank", style={'color': 'blue'}))
                sent_id = "Chunk: " + str(chunk_id)
                return sent_example, sent_id, chunk_id
            else:
                link = create_link(archive.lower(), interview_id.lower(), chunk_start_time, link_tape)
                sent_example.append("\n")
                sent_example.append(html.A(link, href=link, target="_blank", style={'color': 'blue'}))


    sent_id = "Chunk: " + str(chunk_id)
    print(link)
    return sent_example, sent_id, chunk_id
