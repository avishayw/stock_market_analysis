import pandas
import pandas_gbq


def load_df_to_table(df, project_id="avish-analysis", table_id='finviz_data.finviz_data'):
    pandas_gbq.to_gbq(df, table_id, project_id=project_id)