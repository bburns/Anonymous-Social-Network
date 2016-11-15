

def dbClear(db):
    """
    Delete ALL tables in the datastore.
    """
    
    # you actually have to clear the association tables also -
    # even if you delete all the related objects, the association objects
    # are still there!
    # which makes sense, as appengine doesn't know they're just association objects.
    tables = [Student, Class, Book, Paper, Internship, Place, Game]
    tables += [StudentClass, StudentBook, StudentPaper, StudentInternship, StudentPlace, StudentGame]
    for table in tables:
        query = table.all()
        db.delete(query)


