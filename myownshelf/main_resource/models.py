from django.db import models
from django.core.exceptions import ValidationError


def validate_isbn(isbn):
    if len(isbn) not in (10, 13):
        raise ValidationError('ISBN must have 10 or 13 digits.', params={'ISBN': isbn})

    digits = []
    try:
        for char in isbn:
            digits.append(int(char))
    except ValueError:
        raise ValidationError('ISBN can contains only digits.', params={'ISBN': isbn})

    checksum = 0
    if len(digits) == 10:
        for index, digit in enumerate(digits[:-1]):
            checksum += digit * (index + 1)
    else:
        for index, digit in enumerate(digits[:-1]):
            # multiplier: 1 for even and 3 for odd index
            multiplier = (index % 2) * 2 + 1
            checksum += digit * multiplier
    if checksum != digits[-1]:
        raise ValidationError('ISBN is incorrect.', params={'ISBN': isbn})


class VerificationRequiring(models.Model):
    is_verified = models.BooleanField(default=False)

    def verify(self):
        pass

    class Meta:
        abstract = True


class CollectionItem(VerificationRequiring):
    class Meta:
        abstract = True


class Author(VerificationRequiring):
    first_name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)

    def __str__(self):
        return '%s %s' % (self.first_name, self.surname)


class BookGenre(VerificationRequiring):
    name = models.CharField(max_length=50)


class Book(CollectionItem):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    genre = models.ManyToManyField(
        BookGenre,
        through='Book_BookGenre',
        through_fields=('book', 'book_genre')
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class BookEdition(VerificationRequiring):
    # TODO MEDIA_ROOT: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MEDIA_ROOT
    # TODO MEDIA_ROOT: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload_to
    # TODO ISBN10 / ISBN13
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    release_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True, validators=[validate_isbn])
    publisher = models.CharField(max_length=100)


class Book_BookGenre(VerificationRequiring):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_genre = models.ForeignKey(BookGenre, on_delete=models.CASCADE)
