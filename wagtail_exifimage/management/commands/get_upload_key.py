import djclick as click

from wagtail_exifimage.models import ImageUploadAccessKey


@click.command()
@click.argument("username")
def get_upload_key(username):
    key = ImageUploadAccessKey.get_key(username)
    click.secho(f"Key for {username} is {key}", fg="red")
