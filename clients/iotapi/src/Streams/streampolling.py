from itertools import groupby
from Settings.mapiconnection import fetch_streams
from Utilities.customthreading import PeriodicalThread
from datatypes import *
from streams import IOTStream
from streamscontext import Streams_Context

SWITCHER = [{'types': ['clob', 'url'], 'class': 'TextType'},
            {'types': ['char', 'varchar'], 'class': 'LimitedTextType'},
            {'types': ['tinyint', 'smallint', 'int', 'bigint'], 'class': 'SmallIntegerType'},
            {'types': ['hugeint'], 'class': 'HugeIntegerType'},
            {'types': ['real', 'double'], 'class': 'FloatType'},
            {'types': ['decimal'], 'class': 'DecimalType'},
            {'types': ['boolean'], 'class': 'BooleanType'},
            {'types': ['date'], 'class': 'DateType'},
            {'types': ['time', 'timetz'], 'class': 'TimeType'},
            {'types': ['timestamp', 'timestamptz'], 'class': 'TimestampType'},
            {'types': ['inet'], 'class': 'INetType'},
            {'types': ['uuid'], 'class': 'UUIDType'}]


def init_stream_polling_thread(interval):
    thread = PeriodicalThread(interval=interval, worker_func=stream_polling)
    thread.start()


# elem[0] is schema. elem[1] is name, elem[2] is column name, elem[3] is type, elem[4] is type_digits
# elem[5] is type_scale elem[6] is default value elem[7] is nullable
def stream_polling():
    array = fetch_streams()  # TODO check whenever stream's columns are updated
    retained_streams = []
    new_streams = {}
    current_streams = Streams_Context.get_existing_streams()

    if array is not None:
        for key, group in groupby(array, lambda x: Streams_Context.get_context_entry_name(x[0], x[1])):
            if key not in current_streams:
                columns = {}

                for elem in group:
                    for entry in SWITCHER:  # allocate the proper type wrapper
                        if elem[3] in entry['types']:
                            reflection_class = globals()[entry['class']]  # import everything from datatypes!!!
                            new_column = reflection_class(*elem[2:])
                            columns[elem[2]] = new_column  # add new column to the dictionary
                            break
                new_streams[key] = IOTStream(schema_name=elem[0], stream_name=elem[1], columns=columns)
            else:
                retained_streams.append(key)

    Streams_Context.merge_context(retained_streams, new_streams)
