"""
This file is used to generate the graphs for the project. It contains all of
the functions that go from an input that looks something like this:

datalist = ["GDPC1", "GDPPOT"]
chart_title = "GDP vs. Potential GDP, 2006-2010 + 2018-2024"
fig = create_line_graph(datalist, chart_title = chart_title,
                                         legend_titles = ['Real GDP', 
                                                          'Real Potential GDP'],
                                         start_date = '2006-01-01',
                                         end_date = '2012-09-01',
                                         y_axis_title = "Billions of Dollars",
                                         y_axis_range = [15000, 24000],
                                         two_time_periods = True,
                                         second_start_date = '2018-01-01',
                                         second_end_date = '2024-09-01',
                                         fomc = False,
                                         recessions = False,
                                        )   

fig.show() 

to an graph that's outputted as a .png file.

Full input instructions can be found in the README.md file.
"""

# TODO: Add all the functions from Collab notebooks
# TODO: Change output functions to save files to downloads folder.