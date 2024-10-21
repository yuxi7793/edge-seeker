from zipline.pipeline import CustomFactor
import numpy as np
import pytz

class ScoreFactor(CustomFactor):
    window_length = 1
    inputs = []
    dtype = float
    scores = None

    def compute(self, today, assets, out, *inputs):        
        today = today.tz_localize('UTC')
        print(f'today changed to {today}')
        #out[:] = ScoreFactor.scores.loc[today].reindex(assets, fill_value=np.nan).values
        # Check if the ScoreFactor.scores index is timezone-aware and if it is in UTC
        if ScoreFactor.scores.index.tz is None:
            print("The index is not timezone-aware. Localizing to 'UTC'.")
            # Localize the index to UTC
            ScoreFactor.scores.index = ScoreFactor.scores.index.tz_localize('UTC')
        elif ScoreFactor.scores.index.tz != pytz.UTC:
            print(f"The index is timezone-aware but is {ScoreFactor.scores.index.tz} and not in 'UTC'. Converting to 'UTC'.")
            # Convert the index to UTC
            ScoreFactor.scores.index = ScoreFactor.scores.index.tz_convert('UTC')
        else:
            print("The index is already in 'UTC'.")

        # Example of safely accessing the scores
        try:
            today_data = ScoreFactor.scores.loc[today].reindex(assets, fill_value=np.nan)
            out[:] = today_data.values
        except KeyError as e:
            print(f"KeyError: {e} - The requested date '{today}' is not available in scores.")
            # Handle missing date by setting to NaN
            out[:] = np.nan


class IsFilingDateFactor(CustomFactor):
    window_length = 1
    inputs = []
    dtype = float
    scores = None

    def compute(self, today, assets, out, *inputs):
        is_filing_date = ((ScoreFactor.scores != ScoreFactor.scores.shift(1)) & ScoreFactor.scores.notna())
        #print(f'today incoming {today}')
        today = today.tz_localize('UTC')
        #print(f'today changed to {today}')
        out[:] = is_filing_date.loc[today].reindex(assets, fill_value=np.nan).values