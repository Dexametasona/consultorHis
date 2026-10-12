import database.database as db
from ui.interface import initInterface
from his.clientHis import ClientHIS

def main():
    db.createTable()
    client = ClientHIS()
    root = initInterface(client)
    root.mainloop()
    
if __name__ == "__main__":
    main()