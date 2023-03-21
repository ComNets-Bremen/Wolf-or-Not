import sqlite3
from sqlite3 import Error
import sys
import os
from wolves.near_duplicates import CNN

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def get_files_list(conn) -> list:
    sql = "SELECT simplelabel_image.image FROM simplelabel_image JOIN simplelabel_dataset ON"\
    " simplelabel_image.image_dataset_id = simplelabel_dataset.id WHERE simplelabel_dataset.dataset_active"
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    return [i[0] for i in res]

def update_duplicates(conn, to_update, replaced_by):
    print(to_update + " : " +replaced_by)
    with conn:
        sql = "UPDATE simplelabel_image SET image_duplicate_id = ? WHERE image = ?"
        cur = conn.cursor()
        cur.execute(sql, (replaced_by, to_update))
        conn.commit()

def reset_duplicate_column(conn):
    with conn:
        sql = "UPDATE simplelabel_image SET image_duplicate_id = null WHERE "\
        "simplelabel_image.image_dataset_id = (SELECT image_dataset_id FROM simplelabel_dataset WHERE dataset_active)"
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
def detect_near_duplicates():
    conn = create_connection("db.sqlite3")
    files_list = get_files_list(conn)
    to_delete = CNN.find_duplicates("", threshold=0.93, scores=False, use_cuda=False, files_list=files_list)
    print(to_delete)
    reset_duplicate_column(conn)
    for to_update, replaced_by in to_delete.items():
        update_duplicates(conn, to_update, replaced_by)




if __name__ == "__main__":
    detect_near_duplicates()