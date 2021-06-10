# To hide the code for the widget: https://stackoverflow.com/questions/59269548/how-to-hide-ipywidget-code-in-jupyter-notebook

import ipywidgets as widgets
import plotly.graph_objects as go
import numpy as np
import pandas as pd


# Fetch and prep the data
# read in the data from the prepared CSV file. 
co2_data_source = "./data/monthly_in_situ_co2_mlo.csv"
co2_data_full = pd.read_csv(
    co2_data_source, skiprows=np.arange(0, 56), na_values="-99.99"
)

co2_data_full.columns = [
    "year", "month", "date_int", "date", "raw_co2", "seasonally_adjusted",
    "fit", "seasonally_adjusted_fit", "co2 filled", "seasonally_adjusted_filled" 
]

# for handling NaN's see https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
co2_data = co2_data_full.dropna()

# A linear model with slope and intercept to predict CO2
def predict_co2(slope, intercept, initial_date, prediction_date):
    a = slope * (prediction_date-initial_date) + intercept
    return a


#end points for the sliders
slope_endpoints = [0, 3]
intcpt_endpoints = [250, 320]

# Initializing the widgets
slope_first_slider = widgets.FloatSlider(value = 2, min=slope_endpoints[0], max=slope_endpoints[1], step=0.05, readout=False)
slope_last_slider = widgets.FloatSlider(value = 1.65, min=slope_endpoints[0], max=slope_endpoints[1], step=0.05, readout=False) 
intcpt_first_slider = widgets.FloatSlider(value=312, min=intcpt_endpoints[0], max=intcpt_endpoints[1], step=0.25, readout=False)
intcpt_last_slider = widgets.FloatSlider(value=312, min=intcpt_endpoints[0], max=intcpt_endpoints[1], step=0.25, readout=False) 
signal_type_radiobuttons = widgets.RadioButtons(value='Seasonally adjusted data', options=['Seasonally adjusted data', 'Raw data'])
years_radiobuttons = widgets.RadioButtons(value='first 5 years', options=['first 5 years', 'last 5 years', 'All data'])
slope_first_label = widgets.Label("Slope (for first 5 years):")
slope_last_label = widgets.Label("Slope (for last 5 years):")
intcpt_first_label = widgets.Label("Intercept (for first 5 years):")
intcpt_last_label = widgets.Label("Intercept (for last 5 years):")
signal_type_label = widgets.Label("Signal type:")

#Slider labels
slope_first_start = widgets.Label(str(slope_endpoints[0]))
slope_first_end = widgets.Label(str(slope_endpoints[1]))
slope_last_start = widgets.Label(str(slope_endpoints[0]))
slope_last_end = widgets.Label(str(slope_endpoints[1]))
intcpt_first_start = widgets.Label(str(intcpt_endpoints[0]))
intcpt_first_end = widgets.Label(str(intcpt_endpoints[1]))
intcpt_last_start = widgets.Label(str(intcpt_endpoints[0]))
intcpt_last_end = widgets.Label(str(intcpt_endpoints[1]))
slope_first_output = widgets.Label(str("{:.2f}".format(slope_first_slider.value)))
slope_last_output = widgets.Label(str("{:.2f}".format(slope_last_slider.value)))
intcpt_first_output = widgets.Label(str("{:.2f}".format(intcpt_first_slider.value)))
intcpt_last_output = widgets.Label(str("{:.2f}".format(intcpt_last_slider.value)))

def update_graph(slope_first, intcpt_first, slope_last, intcpt_last, signal_type, years):
    #using batch.update makes the plot update more smoothly
    with plot.batch_update():
        # Updating specific traces using their index in plot.data
        if signal_type == 'Raw data':
            plot.data[0].x = co2_data.date
            plot.data[0].y = co2_data.raw_co2
        elif signal_type == 'Seasonally adjusted data':
            plot.data[0].x = co2_data.date
            plot.data[0].y = co2_data.seasonally_adjusted
        
        l1 = slope_first * (co2_data.date - np.min(co2_data.date)) + intcpt_first
        l2 = slope_last * (co2_data.date - np.min(co2_data.date)) + intcpt_last

        plot.data[1].x = co2_data.date
        plot.data[1].y = l1
        
        plot.data[2].x = co2_data.date
        plot.data[2].y = l2

        update_axes_limits(years)

        predicted_co2_first = predict_co2(slope_first, intcpt_first, 1958, 2030)
        predicted_co2_last = predict_co2(slope_last, intcpt_last, 1958, 2030)
        plot.layout.title = f"""Predicted CO2 for {2030} (based on linear fit for <b>first</b> 5 years): {predicted_co2_first:1.2f} ppm.<br>
    Predicted CO2 for {2030} (based on linear fit for <b>last</b> 5 years): {predicted_co2_last:1.2f} ppm."""
    
    
    
def initialize_graph(slope_first, intcpt_first, slope_last, intcpt_last, signal_type, years):
    # Initializing traces with plot.add_trace
    if signal_type == 'Raw data':
        plot.add_trace(go.Scatter(x=co2_data.date, y=co2_data.raw_co2, mode='markers',
            line=dict(color='MediumTurquoise'), name="CO2"))
    elif signal_type == 'Seasonally adjusted data':
        plot.add_trace(go.Scatter(x=co2_data.date, y=co2_data.seasonally_adjusted, mode='markers',
            line=dict(color='MediumTurquoise'), name="CO2"))
    
    l1 = slope_first * (co2_data.date - np.min(co2_data.date)) + intcpt_first
    l2 = slope_last * (co2_data.date - np.min(co2_data.date)) + intcpt_last
           
    plot.add_trace(go.Scatter(x=co2_data.date, y=l1, mode='lines',
        line=dict(color='SandyBrown'), name="linear fit (for first 5 years)"))

    plot.add_trace(go.Scatter(x=co2_data.date, y=l2, mode='lines',
        line=dict(color='MediumVioletRed'), name="linear fit (for last 5 years)"))

    plot.update_layout(xaxis_title='Year', yaxis_title='ppm')

    update_widget_display(years)
    update_axes_limits(years)
    
    predicted_co2_first = predict_co2(slope_first, intcpt_first, 1958, 2030)
    predicted_co2_last = predict_co2(slope_last, intcpt_last, 1958, 2030)
    plot.layout.title = f"""Predicted CO2 for {2030} (based on linear fit for <b>first</b> 5 years): {predicted_co2_first:1.2f} ppm.<br>
Predicted CO2 for {2030} (based on linear fit for <b>last</b> 5 years): {predicted_co2_last:1.2f} ppm."""

#change the visibility of a given list of widgets to the given display type ("flex" for visible or "none" for invisible)
def update_visibility(widget_array, display):
    for w in widget_array:
        w.layout.display = display
        
def update_widget_display(years):
    if years == 'first 5 years':
        update_visibility([slope_first_slider, intcpt_first_slider, slope_first_label, intcpt_first_label, slope_first_output, 
                           slope_first_start, slope_first_end, intcpt_first_output, intcpt_first_start, intcpt_first_end], 'flex')
        update_visibility([slope_last_slider, intcpt_last_slider, slope_last_label, intcpt_last_label, slope_last_output, 
                           slope_last_start, slope_last_end, intcpt_last_output, intcpt_last_start, intcpt_last_end], 'none')
    elif years == 'last 5 years':
        update_visibility([slope_last_slider, intcpt_last_slider, slope_last_label, intcpt_last_label, slope_last_output, 
                           slope_last_start, slope_last_end, intcpt_last_output, intcpt_last_start, intcpt_last_end], 'flex')
        update_visibility([slope_first_slider, intcpt_first_slider, slope_first_label, intcpt_first_label, slope_first_output, 
                           slope_first_start, slope_first_end, intcpt_first_output, intcpt_first_start, intcpt_first_end], 'none')
    elif years == 'All data':
        update_visibility([slope_last_slider, intcpt_last_slider, slope_last_label, intcpt_last_label, slope_last_output, 
                           slope_last_start, slope_last_end, intcpt_last_output, intcpt_last_start, intcpt_last_end,
                           slope_first_slider, intcpt_first_slider, slope_first_label, intcpt_first_label, slope_first_output, 
                           slope_first_start, slope_first_end, intcpt_first_output, intcpt_first_start, intcpt_first_end], 'flex')
    
# Change the x and y axis limits based on which year radiobutton is selected.
def update_axes_limits(years):
    if years == 'first 5 years':
        plot.update_xaxes(range=[1958, 1963])
        plot.update_yaxes(range=[312, 322])
    elif years == 'last 5 years':
        plot.update_xaxes(range=[2015, 2020])
        plot.update_yaxes(range=[395, 415])
    elif years == 'All data':
        plot.update_xaxes(range=[1955, 2023])
        plot.update_yaxes(range=[310, 440])

        
#functions, linked to the widgets, to update the plot when a widget is changed
def slope_first_eventhandler(change):
    update_graph(change.new, intcpt_first_slider.value, slope_last_slider.value, intcpt_last_slider.value, signal_type_radiobuttons.value, years_radiobuttons.value)
    slope_first_output.value = str("{:.2f}".format(change.new))
def slope_last_eventhandler(change):
    update_graph(slope_first_slider.value, intcpt_first_slider.value, change.new, intcpt_last_slider.value, signal_type_radiobuttons.value, years_radiobuttons.value)
    slope_last_output.value = str("{:.2f}".format(change.new))
def intcpt_first_eventhandler(change):
    update_graph(slope_first_slider.value, change.new, slope_last_slider.value, intcpt_last_slider.value, signal_type_radiobuttons.value, years_radiobuttons.value)
    intcpt_first_output.value = str("{:.2f}".format(change.new))
def intcpt_last_eventhandler(change):
    update_graph(slope_first_slider.value, intcpt_first_slider.value, slope_last_slider.value, change.new, signal_type_radiobuttons.value, years_radiobuttons.value)
    intcpt_last_output.value = str("{:.2f}".format(change.new))
def signal_type_eventhandler(change):
    update_graph(slope_first_slider.value, intcpt_first_slider.value, slope_last_slider.value, intcpt_last_slider.value, change.new, years_radiobuttons.value)
def years_eventhandler(change):
    update_widget_display(change.new) #change visibility of sliders and labels
    update_graph(slope_first_slider.value, intcpt_first_slider.value, slope_last_slider.value, intcpt_last_slider.value, signal_type_radiobuttons.value, change.new)


#link the widgets to the appropriate event handler functions above
slope_first_slider.observe(slope_first_eventhandler, 'value')
slope_last_slider.observe(slope_last_eventhandler, 'value')
intcpt_first_slider.observe(intcpt_first_eventhandler, 'value')
intcpt_last_slider.observe(intcpt_last_eventhandler, 'value')
signal_type_radiobuttons.observe(signal_type_eventhandler, 'value')
years_radiobuttons.observe(years_eventhandler, 'value')



#Initialize plot
#Tutorial for FigureWidget and updating the plots: https://www.tutorialspoint.com/plotly/plotly_figurewidget_class.htm
plot = go.FigureWidget()
initialize_graph(slope_first_slider.value, intcpt_first_slider.value, slope_last_slider.value, intcpt_last_slider.value, signal_type_radiobuttons.value, years_radiobuttons.value)

#Formatting widgets
#This is essentially a table with two rows. The first row has two columns of widgets (sliders, labels, radiobuttons),
# and the second row has the graph.

vbox1 = widgets.VBox([widgets.HBox([slope_first_label, slope_first_output]),
                      widgets.HBox([slope_first_start, slope_first_slider, slope_first_end]), 
                      widgets.HBox([slope_last_label, slope_last_output]), 
                      widgets.HBox([slope_last_start, slope_last_slider, slope_last_end]), 
                      signal_type_label, 
                      signal_type_radiobuttons
                     ])

vbox2 = widgets.VBox([widgets.HBox([intcpt_first_label, intcpt_first_output]), 
                      widgets.HBox([intcpt_first_start, intcpt_first_slider, intcpt_first_end]), 
                      widgets.HBox([intcpt_last_label, intcpt_last_output]),
                      widgets.HBox([intcpt_last_start, intcpt_last_slider, intcpt_last_end]),
                      widgets.Label(""),
                      years_radiobuttons
                     ])

hbox = widgets.HBox([vbox1, vbox2], layout=widgets.Layout(display='flex', flex_flow='row', justify_content='space-around', width='100%'))

display(widgets.VBox([hbox, plot]))