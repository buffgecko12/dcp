import test_setup

from wakemeup.models import School

if __name__ == '__main__':
    
    # Create new school
    newschool = School(None, 'MySchool', '123 Fake Ln', 'San Diego', 'CA')
    
    # Save school
    newschoolid = newschool.save()
    
    # Get school
    newschool_new = School.objects.get(newschoolid)
    
    # Get all schools
    allschools = School.objects.all()
    for myschool in allschools:
        print(myschool.schooldisplayname)

    # Update school
    newschool_new.address = '123 New address'
    newschool_new.save()

    # Delete school
    newschool_new.delete()
