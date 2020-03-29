import plotly as py
import csv
import math


def read_file(filename, targetlist):
    with open(filename, newline='') as csvfile:
        x = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in x:
            targetlist.append(row)


def parse_data(descriptor, dataset, labels=[]):
    i = dataset[0].index(descriptor)
    values = [0 for i in range(len(labels))]

    for j in range(1, len(dataset)):
        try:
            values[labels.index(dataset[j][i])] += 1
        except ValueError:
            if not dataset[j][i] == '':
                labels.append(dataset[j][i])
                values.append(1)
        except IndexError:
            if not dataset[j][i] == '':
                labels.append(dataset[j][i])
                values.append(1)
    return labels, values


def parse_data_by_gender(descriptor, dataset):
    i = dataset[0].index(descriptor) # index of the main question within the first list
    x = safety_data[0].index('Gender') # index of the blocking element within the first list, e.g. gender

    labels = []

    values = {
        'Female': [],
        'Male': []
    }

    for j in range(1, len(dataset)):
        try:
            if safety_data[j][x] == 'Female':
                values['Female'][labels.index(dataset[j][i])] += 1
            else:
                values['Male'][labels.index(dataset[j][i])] += 1
        except ValueError:
            if not dataset[j][i] == '':
                labels.append(dataset[j][i])
                if safety_data[j][x] == 'Female':
                    values['Female'].append(1)
                    values['Male'].append(0)
                else:
                    values['Female'].append(0)
                    values['Male'].append(1)

    return labels, values


def format_descrip(src):
    return ''.join(' ' + x if x.isupper() else x for x in src).strip(' ')


def display_axes(x_axis, y_axis='Number of Students'):  # Called in bar graphs and scatter plots
    fig['layout']['xaxis'] = {
        'title': format_descrip(x_axis)
    }
    fig['layout']['yaxis'] = {
        'title': format_descrip(y_axis)
    }


def display(type, data, title, graph_name):  # Called in all graphing functions. Sets necessary elements and displays graph.
    fig['layout']['title']['text'] = title
    fig['data'] = data

    if type == 'grouped_bar_chart':
        fig['layout']['barmode'] = 'group'
    else:
        fig['layout'].pop('barmode', None)  # deletes 'barmode' key if present in the layout dict

    py.offline.plot(fig, filename=graph_name + '.html')


def bar_chart(title, descriptor, dataset, color='#FEBFB3'):
    labels, values = parse_data(descriptor, dataset)

    display_axes(descriptor)
    display('bar_chart', [{
        'type': 'bar',
        'x': labels,
        'y': values,
        'marker': {'color': color},
        'hoverinfo': 'y'
    }], title, 'simplebar')


def grouped_bar_chart(title, descriptor, dataset, colors=['#FEBFB3', '#E1396C']):
    labels, values = parse_data_by_gender(descriptor, dataset)
    l = []
    for (i, color) in zip(values.keys(), colors):
        l.append(
            {
                'type': 'bar',
                'name': i,
                'x': labels,
                'y': values[i],
                'marker': {'color': color},
                'hoverinfo': 'name+y'
            }
        )

    display_axes(descriptor)
    display('grouped_bar_chart', l, title, 'bar')


def simple_scatter(title, descriptor1, descriptor2, dataset1, dataset2, colors=['#FEBFB3', '#E1396C']):
    a = dataset1[0].index(descriptor1)
    b = dataset2[0].index(descriptor2)

    points = []
    counts = []

    for j in range(1, len(dataset1)): # assumes both datasets are the same length
        try:
            counts[points.index([int(dataset1[j][a][0:2]), int(dataset1[j][b][0:2])])] += 1
        except ValueError:
            if not dataset1[j][a][0:2] == '' and not dataset1[j][b][0:2] == '':
                points.append([int(dataset1[j][a][0:2]), int(dataset1[j][b][0:2])])
                counts.append(1)

    display_axes(descriptor1, descriptor2)
    fig['layout']['hovermode'] = 'closest'
    display('simple_scatter', [
        {
            'x': list(map(lambda x: int(x[0]), points)),
            'y': list(map(lambda x: int(x[1]), points)),
            'text': list(map(lambda x: str(x) + " students", counts)),
            'mode': 'markers',
            'marker': {
                'size': list(map(lambda x: math.log(x)*10, counts)),
                'sizemin': 5
            },
            'hoverinfo': 'text',  # HOW TO ADD SIZE?
        }
    ], title, 'scatter')


def pie_chart(descriptor, dataset,
              title,
              x=[0,0.5],
              y=[0.05,.95],
              position='top center', known_values=[]):
    labels, values = parse_data(descriptor, dataset, known_values)

    colors = ['#FEBFB3', '#E1396C', '#96D38C', '#D0F9B1', '#537a4d']

    return {
        'labels': labels,
        'values': values,
        'type': 'pie',
        'marker': {'colors': colors},
        'name': descriptor,
        'domain': {'x': x,
                   'y': y},
        'hoverinfo': 'label+percent',
        'textinfo': 'none',
        'title': {
            'text': title,
            'position': position,
            'font': {
                'size': 20
            }
        }
    }


def main():
    global games_data
    global safety_data

    games_data = []
    safety_data = []

    read_file('Mobilize_GamesCivic_2008.csv', games_data)
    read_file('Mobilize_SchoolSafety_2011.csv', safety_data)

    global fig
    fig = {
        'data': [],
        'layout': {
            'title': {
                'font': {
                    'size': 30,
                    'color': '#7f7f7f'
                }
            },
            'showlegend': True,
        }
    }

    pie1 = pie_chart('OthersHateful', games_data, 'Frequency With Which Students See Others Being Hateful, Racist, or '
                                                  'Sexist While Video Gaming')
    display('grouped_pie_chart', [pie1, pie_chart('OthersIntercede', games_data,
                                                  'Frequency With Which Players See Others Asking for Hateful Actions '
                                                  'to Stop',
                                                  x=[0.5,1], position='bottom center', known_values=pie1['labels'])],
            'Gamer Hate: What Happens While Playing Computer or Console Games', 'pie')
    grouped_bar_chart('Number of Days Students Felt Too Unsafe to Go to School', 'DaysUnsafe',
                      safety_data)
    grouped_bar_chart('During the past 12 months, have you ever been electronically bullied?', 'BulliedElec',
                      safety_data, colors=['#96D38C', '#D0F9B1'])
    bar_chart('How Often Teenagers Play Games', 'HowOften', games_data)
    simple_scatter('Days of School Skipped Out of Fear for Personal Safety Vs. Age', 'Age', 'DaysUnsafe',
                   safety_data, safety_data)


main()