import pandas as pd
import argparse

def merge_files(file1, file2, output, merge_type='inner'):
    """
    Merge two CSV files based on 'id' column and save the result.
    
    Args:
        file1: Path to first CSV file
        file2: Path to second CSV file
        output: Path for the output merged CSV
        merge_type: Type of merge ('inner', 'left', 'right', or 'outer')
    """
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    merged = df1.merge(df2, on='id', how=merge_type)
    merged.to_csv(output, index=False)
    print(f"Merged files saved to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge two CSV files based on id column")
    parser.add_argument("file1", help="Path to the first CSV file")
    parser.add_argument("file2", help="Path to the second CSV file")
    parser.add_argument("output", help="Path for the output merged CSV file")
    parser.add_argument("--merge-type", choices=["inner", "left", "right", "outer"], 
                        default="inner", help="Type of merge to perform (default: inner)")
    
    args = parser.parse_args()
    
    merge_files(args.file1, args.file2, args.output, args.merge_type)
