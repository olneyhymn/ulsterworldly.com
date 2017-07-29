SASSDIR='themes/bootstrap/static/assets/sass'
COMPILEDCSSDIR='themes/bootstrap/static/assets/_css'
S3_BUCKET='presbyterianarchives.com'

all:
	echo "Fail"

build:
	cd themes/westminsterhist && npm run build
	hugo

scss:
	echo "Fail"

preview:
	# Launch local server to preview pages (with auto refresh)
	hugo server --watch --port 1313 --buildDrafts --buildFuture --quiet

clean:
	# Delete local build
	rm -rf public

deploy: build
	# Deploy site to heroku
	s3cmd sync --acl-public --delete-removed public/ s3://$(S3_BUCKET)

push:
	# Push to github
	git push

pdfs:
	# Generate PDFs from HTML pages (esp opc.org pages)
	. make_pdfs.sh

archive_pdfs:
	# Archive pdf files from other sites... just in case.
	. archive_pdfs.sh
