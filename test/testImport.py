#!/usr/bin/env python

# -------------------------------
# testImport.py
# Copyright (C) 2010
# Jonathan Grimes
# -------------------------------

# -------
# imports
# -------

import unittest
from google.appengine.ext import db
from models import *
from utils.xmlImport import *



# -----------
# TestImport
# -----------


class testImport (unittest.TestCase) :

    #. move this to utils
    def dbClear(self):
        "A helper method to clear the database"

        # clear ALL the tables
        # this adds roughly a tenth of a second per test
        # you actually have to clear the association tables also -
        # even if you delete all the related objects, the association objects
        # are still there!
        # which makes sense, as appengine doesn't know they're just association objects.
        tables = [Student, Class, Book, Paper, Internship, Place, Game]
        tables += [StudentClass, StudentBook, StudentPaper, StudentInternship, StudentPlace, StudentGame]
        for table in tables:
            query = table.all()
            db.delete(query)


    def testDbClear(self):
        # make sure the db is actually getting cleared
        self.dbClear()
        student = Student()
        student.id_ = "12345"
        student.put()
        book = Book()
        book.title = 'hobbit'
        book.put()
        sb = StudentBook()
        sb.student = student
        sb.book = book
        sb.rating = "92"
        sb.put()
        self.assert_(sb.book.title == 'hobbit')
        self.assert_(student.studentbook_set[0].book.title == 'hobbit')
        self.dbClear()
        books = Book.all()
        books = books.fetch(9)
        self.assert_(len(books)==0)
        sbs = StudentBook.all()
        sbs = sbs.fetch(9)
        self.assert_(len(sbs)==0)


    def testImportStudent(self):

        self.dbClear()
        xmlImportString("<students><student><id>12345678</id><password>brian</password> </student></students>")
        query = Student.all()
        students = query.fetch(999)
        s = students[0]
        self.assert_(s.id_ == "12345678", s.id_)
        self.assert_(s.password == "brian", s.password)


    def testImportNothing(self):

        self.dbClear()
        xmlImportString("<students></students>")
        query = Student.all()
        students = query.fetch(999)
        self.assert_(len(students) == 0)


    # do some tests with line feeds between elements, because it actually changes the dom structure!!


    #. fails - need to catch exception?
    # def testImportNothing2(self):
    #     self.dbClear()
    #     xmlImportString("")
    #     query = Student.all()
    #     students = query.fetch(999)
    #     self.assert_(len(students) == 0)


    def testImportStudentClass(self) :

        self.dbClear()
        xmlImportString("""
<students>
	<student>
		<id>bkornfue</id>
		<password>ben</password>
		<class>
			<unique>52540</unique>
			<course_num>CS 373</course_num>
			<course_name>Software Engineering</course_name>
			<semester>Fall 2010</semester>
			<instructor>Downing</instructor>
			<rating>95</rating>
			<comment>There were many new concepts</comment>
			<grade></grade>
		</class>
		<class>
			<unique>52568</unique>
			<course_num>M340</course_num>
			<course_name>Linear Algebra</course_name>
			<semester>Fall 2010</semester>
			<instructor>Lam</instructor>
			<rating>55</rating>
			<comment></comment>
			<grade></grade>
		</class>
		<class>
			<unique>52485</unique>
			<course_num>CS 341</course_num>
			<course_name>Automata Theory</course_name>
			<semester>Fall 2010</semester>
			<instructor>Rich</instructor>
			<rating>80</rating>
			<comment>Not fun</comment>
			<grade></grade>
		</class>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]
        sclist = student.studentclass_set.fetch(9857437)
        sc = sclist[0]
        c = sc.class_
        self.assert_(sc.rating == "95")
        self.assert_(sc.comment== "There were many new concepts")
        self.assert_(sc.unique == "52540")
        sc2 = sclist[1]
        c2 = sc2.class_
        self.assert_(sc2.rating == "55")
        self.assert_(c2.course_name == "Linear Algebra")

    
    def testImportStudentClass2(self) :
        self.dbClear()
        xmlImportString('<students><student><class><unique>12345</unique><course_num>CS 343</course_num><course_name>AI</course_name><grade>A</grade><rating>93</rating><comment>cool</comment> </class></student></students>')
        query = Student.all()
        students = query.fetch(1)
        student = students[0]
        sclist = student.studentclass_set.fetch(1)
        sc = sclist[0]
        c = sc.class_
        self.assert_(sc.unique == "12345")
        self.assert_(sc.grade == "A")
        self.assert_(sc.rating == "93")
        self.assert_(c.course_num == "CS 343")
        self.assert_(sc.comment == "cool")


    def testImportStudentClass3(self) :
        self.dbClear()
        xmlImportString('<students><student><class><id>foo</id><unique>12345</unique><course_num>CS 343</course_num><course_name>AI</course_name><grade>A</grade><rating>93</rating><comment></comment> </class><class><unique>54321</unique><course_num>CS 373</course_num><grade>F</grade><rating>20</rating><comment>hard</comment></class></student></students>')
        query = Student.all()
        students = query.fetch(1)
        student = students[0]
        sclist = student.studentclass_set.fetch(2)
        sc = sclist[0]
        c = sc.class_
        self.assert_(sc.unique == "12345")
        self.assert_(sc.grade == "A")
        sc2 = sclist[1]
        c2 = sc2.class_
        self.assert_(sc2.unique == "54321")
        self.assert_(sc2.grade == "F")
        self.assert_(sc2.comment == "hard")


    def testImportClass(self):
        # something from all.xml that bombed
        self.dbClear()
        xmlImportString("""
<students>
<student>
           <class>
                   <unique>52540</unique>
                   <course_num>CS 373</course_num>
                   <course_name>Software Engineering</course_name>
                   <semester>Fall 2010</semester>
                   <instructor>Downing</instructor>
                   <rating>60</rating>
                   <comment>Class doesn't progress as quickly as I would like. Also,
                           projects what.</comment>
                   <grade>B</grade>
           </class>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(1)
        student = students[0]
        sclist = student.studentclass_set.fetch(2)
        sc = sclist[0]
        c = sc.class_
        self.assert_(sc.unique == "52540")
        self.assert_(sc.grade == "B")
        self.assert_(sc.rating == "60")
        


    def testImportStudentBook(self) :
        self.dbClear()
        xmlImportString("""
<students>
	<student>
		<id>bkornfue</id>
		<password>ben</password>
		<class>
			<unique>52540</unique>
			<course_num>CS 373</course_num>
			<course_name>Software Engineering</course_name>
			<semester>Fall 2010</semester>
			<instructor>Downing</instructor>
			<rating>95</rating>
			<comment>There were many new concepts</comment>
			<grade></grade>
		</class>
		<book>
			<isbn>4356745290</isbn>
			<title>Automata, Complexity, and Computability</title>
			<author>Elaine Rich</author>
			<rating>97</rating>
			<comment>Long</comment>
		</book>
		<book>
			<isbn>0679736646</isbn>
			<title>Test</title>
			<author>Ben Kornfuehrer</author>
			<rating>90</rating>
			<comment></comment>
		</book>
		<book>
			<isbn>2398476354098</isbn>
			<title>The Big Bang Theory</title>
			<author>Albert Einstein</author>
			<rating>95</rating>
			<comment></comment>
		</book>
		<paper>
			<paper_category>conference</paper_category>
			<title>Cognitive Architectures: Research Issues and Challenges</title>
			<author>Pat Langley, John E. Laird, and Seth Rogers</author>
			<rating>67</rating>
			<comment>2009. Gives a detailed overview of cognitive architectures.</comment>
		</paper>
		<game>
			<os>Any</os>
			<title>Call of Duty: Modern Warfare</title>
			<rating>5</rating>
			<comment>It's a crime to be this good</comment>
		</game>
   </student>
</students>
""")

        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        sblist = student.studentbook_set.fetch(9857437)
        
        #test 1 Book			
        sb = sblist[0]
        b = sb.book
        self.assert_(sb.rating == "97")
        self.assert_(sb.comment == "Long")
        self.assert_(b.isbn == "4356745290")
        self.assert_(b.title == "Automata, Complexity, and Computability", b.title)
        self.assert_(b.author == "Elaine Rich")
        
        #test 2 books
        sb = sblist[1]
        b = sb.book
        self.assert_(sb.rating == "90")
        self.assert_(b.isbn == "0679736646")
        self.assert_(b.title == "Test", b.title)
        self.assert_(b.author == "Ben Kornfuehrer")


    def testImportStudentBook2(self) :
        self.dbClear()
        xmlImportString("""
<students>
   <student><id>12345678</id><password>foo</password></student>
   <student>
	<id>73162312</id>
	<password>brian</password>
	<book>
		<isbn>0679734465</isbn>
		<title>Valis</title>
		<author>Philip K. Dick</author>
		<rating>95</rating>
		<comment>crazy</comment>
	</book>
	<book>
		<isbn>0679736646</isbn>
		<title>Ubik</title>
		<author>Philip K. Dick</author>
		<rating>90</rating>
		<comment></comment>
	</book>
	<book>
		<isbn>0136042597</isbn>
		<title>Artificial Intelligence: A Modern Approach</title>
		<author>Stuart Russell and Peter Norvig</author>
		<rating>95</rating>
		<comment></comment>
	</book>
	<game>
		<os>Apple II</os>
		<title>Ultima I</title>
		<rating>95</rating>
		<comment>I loved this game as a kid.</comment>
	</game>
    </student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[1]
        sblist = student.studentbook_set.fetch(9857437)

        # test 1 Book	
        sb = sblist[0]
        b = sb.book
        self.assert_(sb.rating == "95")
        self.assert_(sb.comment == "crazy")
        self.assert_(b.isbn == "0679734465")
        self.assert_(b.title == "Valis", b.title)
        self.assert_(b.author == "Philip K. Dick")

        # test 2 books
        sb = sblist[1]
        b = sb.book
        self.assert_(sb.rating == "90")
        self.assert_(b.isbn == "0679736646")
        self.assert_(b.title == "Ubik", b.title)
        self.assert_(b.author == "Philip K. Dick")



    def testImportBook(self):
        # something from all.xml that bombed
        self.dbClear()
        xmlImportString("""
<students>
    <student>
          <book>
                      <isbn>0345347951</isbn>
                      <title>Childhood's End</title>
                      <author>Arthur C. Clarke</author>
<rating>90</rating>
<comment></comment>
          </book>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]
        sblist = student.studentbook_set.fetch(9857437)

        # test 1 Book	
        sb = sblist[0]
        b = sb.book
        self.assert_(sb.rating == "90")
        self.assert_(sb.comment == "")
        self.assert_(b.title == "Childhood's End")
        self.assert_(b.author == "Arthur C. Clarke")
        self.assert_(b.isbn == "0345347951")

    
    def testImportStudentPaper(self) :
        self.dbClear()
        xmlImportString("""
<students>
	<student>
		<id>bkornfue</id>
		<password>ben</password>
		<book>
			<isbn>2398476354098</isbn>
			<title>The Big Bang Theory</title>
			<author>Albert Einstein</author>
			<rating>95</rating>
			<comment></comment>
		</book>
		<paper>
			<paper_category>conference</paper_category>
			<title>Cognitive Architectures: Research Issues and Challenges</title>
			<author>Pat Langley, John E. Laird, and Seth Rogers</author>
			<rating>67</rating>
			<comment>2009. Gives a detailed overview of cognitive architectures.</comment>
		</paper>
		<paper>
			<paper_category>journal</paper_category>
			<title>The 1980 ACM Turing Award Lecture</title>
			<author>C.A.R. (Tony) Hoare</author>
			<rating>92</rating>
			<comment>Interesting talk about his experience designing languages</comment>
		</paper>
		<paper>
			<paper_category>journal</paper_category>
			<title>The Evolution of Lisp</title>
			<author>Guy L. Steele, Jr. and Richard P. Gabriel</author>
			<rating>90</rating>
			<comment>ACM 1993</comment>
		</paper>
		<!--
		    live_place
		    eat_place
		    fun_place
		    -->
   </student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        splist = student.studentpaper_set.fetch(9857437)

        #test 1 Paper	
        sp = splist[0]
        p = sp.paper
        self.assert_(sp.rating == "67")
        self.assert_(sp.comment == "2009. Gives a detailed overview of cognitive architectures.")
        self.assert_(p.paper_category == "conference")
        self.assert_(p.title == "Cognitive Architectures: Research Issues and Challenges")
        self.assert_(p.author == "Pat Langley, John E. Laird, and Seth Rogers")

        sp = splist[1]
        p = sp.paper
        self.assert_(sp.rating == "92")
        self.assert_(sp.comment == "Interesting talk about his experience designing languages")
        self.assert_(p.paper_category == "journal")
        self.assert_(p.title == "The 1980 ACM Turing Award Lecture")
        self.assert_(p.author == "C.A.R. (Tony) Hoare")

        sp = splist[2]
        p = sp.paper
        self.assert_(sp.rating == "90")
        self.assert_(sp.comment == "ACM 1993")
        self.assert_(p.paper_category == "journal")
        self.assert_(p.title == "The Evolution of Lisp")
        self.assert_(p.author == "Guy L. Steele, Jr. and Richard P. Gabriel")

    
    def testImportStudentPaper2(self) :
        self.dbClear()
        xmlImportString("""
<students>
    <student>
        <id>bhujkiop</id>
        <password>jonathan</password>
        <book>
            <isbn>0136042597</isbn>
            <title>Artificial Intelligence: A Modern Approach</title>
            <author>Norvig</author>
            <rating>76</rating>
            <comment></comment>
        </book>
        <paper>
            <paper_category>journal</paper_category>
            <title>The New Product Development Game</title>
            <author>Hirotaka Takeuchi and Ikujiro Nanaka</author>
            <rating>83</rating>
            <comment></comment>
        </paper>
</student>
</students>
""")

        query = Student.all()
        students = query.fetch(5)
        student = students[0]
        splist = student.studentpaper_set.fetch(9857437)

        #test 1 Paper	
        sp = splist[0]
        p = sp.paper
        self.assert_(sp.rating == "83")
        self.assert_(sp.comment == "")
        self.assert_(p.paper_category == "journal")
        self.assert_(p.title == "The New Product Development Game")
        self.assert_(p.author == "Hirotaka Takeuchi and Ikujiro Nanaka")



    def testImportStudentInternship(self) :
        self.dbClear()
        xmlImportString("""
<students>
<student>
		<internship>
			<place_name>Microsoft</place_name>
			<location>Seattle</location>
			<semester>Summer 2009</semester>
			<rating>5</rating>
			<comment>asdklfj</comment>
		</internship>
		<internship>
			<place_name>Valero</place_name>
			<location>San Antonio</location>
			<semester>Summer 2010</semester>
			<rating>25</rating>
			<comment>It Sucked!</comment>
		</internship>
		<internship>
			<place_name>Deloitte</place_name>
			<location>Houston</location>
			<semester>Summer 2008</semester>
			<rating>4</rating>
			<comment>Not my major</comment>
		</internship>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        silist = student.studentinternship_set.fetch(9857437)

        #test 1 Internship	
        si = silist[0]
        i = si.internship
        self.assert_(si.rating == "5")
        self.assert_(si.comment == "asdklfj")
        self.assert_(i.place_name == "Microsoft")
        self.assert_(i.location == "Seattle")
        self.assert_(i.semester == "Summer 2009")

        #test 2 Internships
        si = silist[1]
        i = si.internship
        self.assert_(si.rating == "25")
        self.assert_(si.comment == "It Sucked!")
        self.assert_(i.place_name == "Valero")
        self.assert_(i.location == "San Antonio")
        self.assert_(i.semester == "Summer 2010")

        #test 3 Internships
        si = silist[2]
        i = si.internship
        self.assert_(si.rating == "4")
        self.assert_(si.comment == "Not my major")	
        self.assert_(i.place_name == "Deloitte")
        self.assert_(i.location == "Houston")
        self.assert_(i.semester == "Summer 2008")


    """
    def testImportStudentInternship2(self) :

        self.dbClear()
        xmlImportFile('xml/ASN2.xml')
        query = Student.all()
        students = query.fetch(5)
        student = students[0]
        silist = student.studentinternship_set.fetch(9857437)

        #test 1 Internship	
        si = silist[0]
        i = si.internship
        self.assert_(si.rating == "25")
        self.assert_(si.comment == "Beautiful City")	
        self.assert_(i.place_name == "Facebook")
        self.assert_(i.location == "Mountain View")
        self.assert_(i.semester == "Summer 2008")

        #test 2 Internships	
        si = silist[1]
        i = si.internship
        self.assert_(si.rating == "89")
        self.assert_(si.comment == "It was good")
        self.assert_(i.place_name == "uFollowit")
        self.assert_(i.location == "Austin")
        self.assert_(i.semester == "Summer 2009")

        #test 3 Internships
        si = silist[2]
        i = si.internship
        self.assert_(si.rating == "68")
        self.assert_(si.comment == "Too cold in Wisconsin")	
        self.assert_(i.place_name == "Epic")
        self.assert_(i.location == "Madison")
        self.assert_(i.semester == "Summer 2010")
    """

    def testImportStudentStudyPlace(self) :

        self.dbClear()
        xmlImportString("""
<students>
<student>
		<study_place>
			<place_name>Painter</place_name>
			<location>Inner Campus Drive</location>
			<semester>Fall 2010</semester>
			<rating>4</rating>
			<comment>A lot of stairs to walk up</comment>
		</study_place>
		<study_place>
			<place_name>Architecture Library</place_name>
			<location>21st Street</location>
			<semester>Fall 2010</semester>
			<rating>45</rating>
			<comment></comment>
		</study_place>
		<study_place>
			<place_name>PCL</place_name>
			<location>Speedway and 21st</location>
			<semester>Fall 2010</semester>
			<rating>3</rating>
			<comment>Bleh</comment>
		</study_place>
		<live_place>
			<place_name>The Block</place_name>
			<location>23rd Street</location>
			<semester>Fall 2009</semester>
			<rating>20</rating>
			<comment>Twas OK</comment>
		</live_place>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        ssplist5 = student.studentplace_set


        ssplist = []
        for pA in ssplist5:
            if pA.place.place_type == "study_place":
                ssplist.append(pA)	

        #test 1 Study Place	
        ssp = ssplist[0]
        sp = ssp.place
        self.assert_(ssp.rating == "4")
        self.assert_(ssp.comment == "A lot of stairs to walk up")
        self.assert_(sp.place_name == "Painter")
        self.assert_(sp.semester == "Fall 2010")

        #test 2 Study Places	
        ssp = ssplist[1]
        sp = ssp.place
        self.assert_(ssp.rating == "45")
        self.assert_(ssp.comment == "")
        self.assert_(sp.place_name == "Architecture Library")
        self.assert_(sp.semester == "Fall 2010")

        #test 3 Study Places	
        ssp = ssplist[2]
        sp = ssp.place
        self.assert_(ssp.rating == "3")
        self.assert_(ssp.comment == "Bleh")
        self.assert_(sp.place_name == "PCL")
        self.assert_(sp.semester == "Fall 2010")

    """
    def testImportStudentStudyPlace2(self) :

        self.dbClear()
        xmlImportFile('xml/ASN2.xml')
        query = Student.all()
        students = query.fetch(5)
        student = students[3]	
        ssplist5 = student.studentplace_set


        ssplist = []
        for pA in ssplist5:
            if pA.place.place_type == "study_place":
                ssplist.append(pA)

        #test 1 Study Place	
        ssp = ssplist[0]
        sp = ssp.place
        self.assert_(ssp.rating == "4")
        self.assert_(ssp.comment == "No cell phone reception")
        self.assert_(sp.place_name == "ENS")
        self.assert_(sp.semester == "Spring 2010")

        #test 2 Study Places	
        ssp = ssplist[1]
        sp = ssp.place
        self.assert_(ssp.rating == "75")
        self.assert_(ssp.comment == "A good place to sleep")
        self.assert_(sp.place_name == "FAC")
        self.assert_(sp.semester == "Fall 2008")

        #test 3 Study Places	
        ssp = ssplist[2]
        sp = ssp.place
        self.assert_(ssp.rating == "85")
        self.assert_(ssp.comment == "Very quiet since no one knows about it.")
        self.assert_(sp.place_name == "Rec Center")
        self.assert_(sp.semester == "Spring 2009")
    """

    def testImportStudentLivePlace(self) :

        self.dbClear()
        xmlImportString("""
<students>
<student>
		<study_place>
			<place_name>PCL</place_name>
			<location>Speedway and 21st</location>
			<semester>Fall 2010</semester>
			<rating>3</rating>
			<comment>Bleh</comment>
		</study_place>
		<live_place>
			<place_name>The Block</place_name>
			<location>23rd Street</location>
			<semester>Fall 2009</semester>
			<rating>20</rating>
			<comment>Twas OK</comment>
		</live_place>
		<live_place>
			<place_name>Enfield Townhomes</place_name>
			<location>2605 Enfield Rd</location>
			<semester>Spring 2008</semester>
			<rating>45</rating>
			<comment>Peace and quiet</comment>
		</live_place>
		<live_place>
			<place_name>Jefferson 26</place_name>
			<location>26th Street</location>
			<semester>Spring 2009</semester>
			<rating>45</rating>
			<comment>Awesome Pool</comment>
		</live_place>
		<eat_place>
			<place_name>Pluckers</place_name>
			<location>rio grande</location>
			<semester>Spring 2009</semester>
			<rating>45</rating>
			<comment>WINGS</comment>
		</eat_place>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        slplist5 = student.studentplace_set


        slplist = []
        for pA in slplist5:
            if pA.place.place_type == "live_place":
                slplist.append(pA)

        #test 1 Live Place	
        slp = slplist[0]
        lp = slp.place
        self.assert_(slp.rating == "20")
        self.assert_(slp.comment == "Twas OK")
        self.assert_(lp.place_name == "The Block")
        self.assert_(lp.semester == "Fall 2009")

        #test 2 Live Places
        slp = slplist[1]
        lp = slp.place
        self.assert_(slp.rating == "45")
        self.assert_(slp.comment == "Peace and quiet")
        self.assert_(lp.place_name == "Enfield Townhomes")
        self.assert_(lp.semester == "Spring 2008")

        #test 3 Live Places
        slp = slplist[2]
        lp = slp.place
        self.assert_(slp.rating == "45")
        self.assert_(slp.comment == "Awesome Pool")
        self.assert_(lp.place_name == "Jefferson 26")
        self.assert_(lp.semester == "Spring 2009")


    """
    def testImportStudentLivePlace2(self) :

        self.dbClear()
        xmlImportFile('xml/ASN2.xml')
        query = Student.all()
        students = query.fetch(5)
        student = students[3]	
        slplist5 = student.studentplace_set


        slplist = []
        for pA in slplist5:
            if pA.place.place_type == "live_place":
                slplist.append(pA)

        #test 1 Live Place	
        slp = slplist[0]
        lp = slp.place
        self.assert_(slp.rating == "20")
        self.assert_(slp.comment == "I had no car")
        self.assert_(lp.place_name == "University Village")
        self.assert_(lp.semester == "Fall 2007")

        #test 2 Live Places	
        slp = slplist[1]
        lp = slp.place
        self.assert_(slp.rating == "85")
        self.assert_(slp.comment == "Peace and quiet")
        self.assert_(lp.place_name == "Blackstone Apts")
        self.assert_(lp.semester == "Spring 2010")

        #test 3 Live Places	
        slp = slplist[2]
        lp = slp.place
        self.assert_(slp.rating == "90")
        self.assert_(slp.comment == "On Riverside")
        self.assert_(lp.place_name == "Landry Place Apts")
        self.assert_(lp.location == "2239 Cromwell Cir.")
    """

    def testImportStudentEatPlace(self) :

        self.dbClear()
        xmlImportString("""
<students>
<student>
		<live_place>
			<place_name>Jefferson 26</place_name>
			<location>26th Street</location>
			<semester>Spring 2009</semester>
			<rating>45</rating>
			<comment>Awesome Pool</comment>
		</live_place>
		<eat_place>
			<place_name>Pluckers</place_name>
			<location>rio grande</location>
			<semester>Spring 2009</semester>
			<rating>45</rating>
			<comment>WINGS</comment>
		</eat_place>
		<eat_place>
			<place_name>What-A-Burger</place_name>
			<location>Guadalupe</location>
			<semester>Spring 2010</semester>
			<rating>45</rating>
			<comment>Drunken Food</comment>
		</eat_place>    
		<eat_place>
			<place_name>Taco C</place_name>
			<location>MLK</location>
			<semester>Fall 2007</semester>
			<rating>45</rating>
			<comment>3 AM Drunkfest</comment>
		</eat_place>    
		<fun_place>
			<place_name>Dave and Busters</place_name>
			<location>183</location>
			<semester>Spring 2009</semester>
			<rating>45</rating>
			<comment>Eat and Play combo</comment>
		</fun_place>            
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        seplist5 = student.studentplace_set

        seplist = []
        for pA in seplist5:
            if pA.place.place_type == "eat_place":
                seplist.append(pA)

        #test 1 Eat Place	
        sep = seplist[0]
        ep = sep.place
        self.assert_(sep.rating == "45")
        self.assert_(sep.comment == "WINGS")
        self.assert_(ep.place_name == "Pluckers")
        self.assert_(ep.semester == "Spring 2009")

        #test 2 Eat Places	
        sep = seplist[1]
        ep = sep.place
        self.assert_(sep.rating == "45")
        self.assert_(sep.comment == "Drunken Food")
        self.assert_(ep.place_name == "What-A-Burger")
        self.assert_(ep.semester == "Spring 2010")

        #test 3 Eat Places	
        sep = seplist[2]
        ep = sep.place
        self.assert_(sep.rating == "45")
        self.assert_(sep.comment == "3 AM Drunkfest")
        self.assert_(ep.place_name == "Taco C")
        self.assert_(ep.semester == "Fall 2007")

    """
    def testImportStudentEatPlace2(self) :

        self.dbClear()
        xmlImportFile('xml/ASN2.xml')
        query = Student.all()
        students = query.fetch(5)
        student = students[3]	
        seplist5 = student.studentplace_set


        seplist = []
        for pA in seplist5:
            if pA.place.place_type == "eat_place":
                seplist.append(pA)	
        #test 1 Eat Place	
        sep = seplist[0]
        ep = sep.place
        self.assert_(sep.rating == "95")
        self.assert_(sep.comment == "Free Dessert")
        self.assert_(ep.place_name == "Carinos")
        self.assert_(ep.location == "Brodie Lane")

        #test 2 Eat Places	
        sep = seplist[1]
        ep = sep.place
        self.assert_(sep.rating == "83")
        self.assert_(sep.comment == "Thai Food")
        self.assert_(ep.place_name == "Madam Mam's")
        self.assert_(ep.location == "Guadalupe")

        #test 3 Eat Places	
        sep = seplist[2]
        ep = sep.place
        self.assert_(sep.rating == "87")
        self.assert_(sep.comment == "3 AM Drunkfest")
        self.assert_(ep.place_name == "Kerbey Lane")
        self.assert_(ep.semester == "Fall 2006")
    """
   
     
    def testImportStudentFunPlace(self) :

        self.dbClear()
        xmlImportString("""
<students>
<student>
		<fun_place>
			<place_name>Dave and Busters</place_name>
			<location>183</location>
			<semester>Spring 2009</semester>
			<rating>45</rating>
			<comment>Eat and Play combo</comment>
		</fun_place>            
		<fun_place>
			<place_name>Main Event</place_name>
			<location>Anderson Mill</location>
			<semester>Fall 2009</semester>
			<rating>45</rating>
			<comment>Glow in the dark golf</comment>
		</fun_place>
		<fun_place>
			<place_name>Downtown</place_name>
			<location>downtown</location>
			<semester>Spring 2010</semester>
			<rating>45</rating>
			<comment>All the bars in one street</comment>
		</fun_place>
		<game>
			<os>Any</os>
			<title>FIFA 2011</title>
			<rating>5</rating>
			<comment>The players look so real</comment>
		</game>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        sfplist5 = student.studentplace_set

        sfplist = []
        for pA in sfplist5:
            if pA.place.place_type == "fun_place":
                sfplist.append(pA)

        #test 1 Fun Place	
        sfp = sfplist[0]
        fp = sfp.place
        self.assert_(sfp.rating == "45")
        self.assert_(sfp.comment == "Eat and Play combo")
        self.assert_(fp.place_name == "Dave and Busters")
        self.assert_(fp.semester == "Spring 2009")

        #test 2 Fun Places	
        sfp = sfplist[1]
        fp = sfp.place
        self.assert_(sfp.rating == "45")
        self.assert_(sfp.comment == "Glow in the dark golf")
        self.assert_(fp.place_name == "Main Event")
        self.assert_(fp.location == "Anderson Mill")

        #test 3 Fun Places	
        sfp = sfplist[2]
        fp = sfp.place
        self.assert_(sfp.rating == "45")
        self.assert_(sfp.comment == "All the bars in one street")
        self.assert_(fp.place_name == "Downtown")
        self.assert_(fp.semester == "Spring 2010")


    """
    def testImportStudentFunPlace2(self) :

        self.dbClear()
        xmlImportFile('xml/ASN2.xml')
        query = Student.all()
        students = query.fetch(5)
        student = students[3]	
        sfplist5 = student.studentplace_set

        sfplist = []
        for pA in sfplist5:
            if pA.place.place_type == "fun_place":
                sfplist.append(pA)

        #test 1 Fun Place	
        sfp = sfplist[0]
        fp = sfp.place
        self.assert_(sfp.rating == "99")
        self.assert_(sfp.comment == "Events everywhere")
        self.assert_(fp.place_name == "Las Vegas")
        self.assert_(fp.location == "Nevada")

        #test 2 Fun Places	
        sfp = sfplist[1]
        fp = sfp.place
        self.assert_(sfp.rating == "80")
        self.assert_(sfp.comment == "Bowling")
        self.assert_(fp.place_name == "Union Underground")
        self.assert_(fp.location == "Student Union")

        #test 3 Fun Places	
        sfp = sfplist[2]
        fp = sfp.place
        self.assert_(sfp.rating == "97")
        self.assert_(sfp.comment == "Great Music")
        self.assert_(fp.place_name == "ACL")
        self.assert_(fp.semester == "Fall 2010")
    """


    def testImportStudentGame(self) :

        self.dbClear()
        xmlImportString("""
<students>
<student>
		<fun_place>
			<place_name>Downtown</place_name>
			<location>downtown</location>
			<semester>Spring 2010</semester>
			<rating>45</rating>
			<comment>All the bars in one street</comment>
		</fun_place>
		<game>
			<os>Any</os>
			<title>FIFA 2011</title>
			<rating>5</rating>
			<comment>The players look so real</comment>
		</game>
		<game>
			<os>Any</os>
			<title>Call of Duty: Modern Warfare</title>
			<rating>5</rating>
			<comment>It's a crime to be this good</comment>
		</game>
</student>
</students>
""")
        query = Student.all()
        students = query.fetch(5)
        student = students[0]	
        sglist = student.studentgame_set.fetch(9857437)

        #test 1 Game
        sg = sglist[0]
        g = sg.game
        self.assert_(sg.rating == "5")
        self.assert_(sg.comment == "The players look so real")
        self.assert_(g.os == "Any")
        self.assert_(g.title == "FIFA 2011")

        #test 2 Games
        sg = sglist[1]
        g = sg.game
        self.assert_(sg.rating == "5")
        self.assert_(sg.comment == "It's a crime to be this good")
        self.assert_(g.os == "Any")
        self.assert_(g.title == "Call of Duty: Modern Warfare")

    """
    def testImportStudentGame2(self) :

        self.dbClear()
        xmlImportFile('xml/ASN2.xml')
        query = Student.all()
        students = query.fetch(5)
        student = students[3]	
        sglist = student.studentgame_set.fetch(9857437)

        #test 1 Game	
        sg = sglist[0]
        g = sg.game
        self.assert_(sg.rating == "5")
        self.assert_(sg.comment == "Steal cars and make money")
        self.assert_(g.os == "Any")
        self.assert_(g.title == "Grand Theft Auto")

        #test 2 Games	
        sg = sglist[1]
        g = sg.game
        self.assert_(sg.rating == "5")
        self.assert_(sg.comment == "Too many mouse clicks")
        self.assert_(g.title == "World of War Craft")
        self.assert_(g.os == "Any")

        #test 3 Game
        sg = sglist[2]
        g = sg.game
        self.assert_(sg.rating == "5")
        self.assert_(sg.comment == "AMAZING!!")
        self.assert_(g.os == "Any")
        self.assert_(g.title == "Super Smash Brothers")
    """


