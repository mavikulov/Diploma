import pandas as pd
import json
from tqdm import tqdm
from typing import Tuple, List, Dict


SINUS_RHTS = ('STACH', 'SR', 'SARRH', 'SBRAD')
SINUS = ['SR', 'STACH', 'SARRH', 'SBRAD']
NOT_SINUS = ['BIGU', 'PSVT', 'SVARR', 'AFIB', 'AFLT', 'TRIGU', 'PACE', 'SVTAC']


def get_abbrevations(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    required_names = df[df['rhythm'] == 1][['Scp Code Name', 'description']]
    sinus_arrh = required_names[required_names['description'].str.contains('sinus')]
    sinus = list(sinus_arrh['Scp Code Name'])
    not_sinus = list(set(required_names['Scp Code Name']) - set(sinus))
    abbrevations = list(required_names['Scp Code Name'])
    return abbrevations, sinus, not_sinus


def label_column(report: str) -> str:
    is_sinus = False
    is_not_sinus = False
    report = json.loads(report.replace("'", '"'))
    for key, value in report.items():
        if key in SINUS:
            is_sinus = True
        if key in NOT_SINUS:
            is_not_sinus = True
    if is_sinus and is_not_sinus:
        return "Undefined"
    if is_sinus:
        return 'Sinus'
    return 'Not Sinus'


def compute_codes_count(df: pd.DataFrame) -> Dict[str, int]:
    count_values = {key: 0 for key in df['scp_codes']}
    for report in tqdm(df['scp_codes']):
        if type(report) is str:
            report = json.loads(report.replace("'", '"'))
        for key, _ in report.items():
            if key in count_values:
                count_values[key] += 1
    return count_values


def preprocess_data(scp_statements: pd.DataFrame, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    scp_statements.rename(columns={scp_statements.columns[0]: 'Scp Code Name'}, inplace=True)
    df['scp_codes'] = df['scp_codes'].apply(label_column)
    indexes_to_drop = df[df['scp_codes'] == 'Undefined'].index
    prepared_df = df.drop(indexes_to_drop)
    return scp_statements, prepared_df