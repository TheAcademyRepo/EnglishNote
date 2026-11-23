class UserRole:
    STUDENT = "student"
    CONTRIBUTOR = "contributor"
    AUTHOR = "author"
    EDITOR = "editor"
    ADMINISTRATOR = "administrator"
    SUPER_ADMINISTRATOR = "super_administrator"

    CHOICES = [
        (STUDENT, "Student"),
        (CONTRIBUTOR, "Contributor"),
        (AUTHOR, "Author"),
        (EDITOR, "Editor"),
        (ADMINISTRATOR, "Administrator"),
        (SUPER_ADMINISTRATOR, "Super Administrator"),
    ]

    @classmethod
    def all(cls):
        return [
            cls.STUDENT,
            cls.CONTRIBUTOR,
            cls.AUTHOR,
            cls.EDITOR,
            cls.ADMINISTRATOR,
            cls.SUPER_ADMINISTRATOR,
        ]