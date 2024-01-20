import pandas as pd
import pathlib

from .qb_scraper import get_qb_grades

## get package location ##
loc = pathlib.Path(__file__).parent.parent.resolve()

def load_csv(file_name):
    '''
    loads csv. Returns none if not found
    '''
    try:
        return pd.read_csv(
            '{0}/{1}'.format(loc, file_name),
            index_col=0
        )
    except:
        return None
    
def write_csv(df, file_name):
    '''
    writes an updated csv to package
    '''
    df.to_csv(
        '{0}/{1}'.format(loc, file_name)
    )

def update_dataset(existing, new, id_col):
    '''
    compares new data to existing and updates with a dedupe
    '''
    ## concat sets ##
    updated = pd.concat([existing, new])
    return updated.groupby([id_col]).tail(1).reset_index(drop=True)


##############
## WRAPPERS ##
##############
def update_qb_ranks():
    '''
    updates qb rankings csv
    '''
    ## look for existing ##
    existing = load_csv('qb_rankings.csv')
    ## get new grades ##
    new = get_qb_grades()
    ## join ##
    output = new
    if existing is not None:
        output = update_dataset(existing, new, 'grade_id')
    ## write ##
    write_csv(output, 'qb_rankings.csv')
    
