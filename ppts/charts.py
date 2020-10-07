import pandas as pd

from ppts.queries import age_by_record_type


def age_by_record_type_png(category="PRJ"):
    records = age_by_record_type(category)
    data = {
        record.record_id: [
            category,
            record.status,
            record.date_opened,
            record.date_closed,
            record.age
        ]
        for record in records
    }
    df = pd.DataFrame.from_dict(
        data, orient='index',
        columns=['record_type', 'status', 'date_opened', 'date_closed',
                 'age'])
    hist = df.hist(column='age')
    return hist
