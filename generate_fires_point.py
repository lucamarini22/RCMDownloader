import pandas as pd
import csv


def generate_fires_point(
        csv_file: str,
        out_file: str,
        num_rows_before_header: int = 2, 
) -> None:
    """Generates javascript definition of geometry points for Google Earth 
    Engine given a csv file that contains the information about the points of
    the fires.

    Args:
        csv_file (str): path of the csv file.
        out_file (str): path of the output text file containing the javascript
          definition of geometry points.
        num_rows_before_header (int, optional): number of rows before the 
          header in the csv file. Defaults to 2.
    """
    df = pd.read_csv(csv_file)
    df.columns = df.iloc[1]
    # Drops rows before header
    df = df.iloc[num_rows_before_header:]
    
    df['fire_point_def'] = 'var ' \
        + df['Fire number'] \
            + ' = ee.Geometry.Point([' \
                + df['Long'] \
                    + ',' \
                        + df['Lat'] + ']);'

    df['fire_point_def'].to_csv(
        out_file, 
        index=False, 
        header=False, 
        doublequote=False,
        quoting=csv.QUOTE_NONE,
        escapechar='\\',
        sep = '\n'
    )
    

    


if __name__ == "__main__":
    csv_file = r'C:\Users\lucamar\alberta_fires.csv'
    out_file = r'C:\Users\lucamar\alberta_fires_point_def.txt'

    generate_fires_point(csv_file, out_file)