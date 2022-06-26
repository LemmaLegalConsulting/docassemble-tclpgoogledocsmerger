# docassemble.tclpgoogledocsmerger

A docassemble extension that helps a user search for docs in a Google Drive based on tags / metadata.

Made in association with The [Chancery Lane Project](https://chancerylaneproject.org/)

Special dependencies:

* a branch of [docxcompose](https://github.com/BryceStevenWilley/docxcompose/tree/master), version `1.3.5-devlemma`.
  * this branch merges a [standing PR](https://github.com/4teamwork/docxcompose/pull/58) that works when certain styles aren't present
  * also fixes some issues with [abstractNumId uniqueness](https://github.com/BryceStevenWilley/docxcompose/commit/a90e445857dbf61ce5c999bb50b13291b51d7b12)
* a branch of [docxtpl](https://github.com/LemmaLegalConsulting/docxtpl/tree/subdoc_bookmark_issues)
  * this branch fixed an issue where bookmark ids were only renumbered per subdocument, not over the whole document

## Airtable Config

This interview uses the data in [an Airtable](https://airtable.com/shr5ITqr8fOECQthj/tblZduZJJkNz9tbzY), to
determine which clause applies to a particular query.

In your docassemble configuration, you should add the following YAML dictionary, replacing the example values on the right with your Airtable information:

```yaml
docs airtable:
  api key: keyabcDEF12345678
  base id: appabcDEF12345678
  table name: "Grid View"
```

If there are issues connecting to the Airtable, those issues will be
printed in the [docassemble logs](https://docassemble.org/docs/admin.html#logs).

## Google Drive Config

In your docassemble configuration, you should add the following YAML key-value pair:

```yaml
drive doc bank: "google-drive-folder-id-abc123"
```

The Google drive folder id should be visible in the URL of the drive folder, after `/u/0/folders/`.

## The Cache

An on server cache of the airtable data and the google drive data is kept. You can directly tinker with this cache
by using the `cache_settings.yml` interview. You must be logged in as a server admin to use that interview.

## Cloud Convert Config

```yaml
cloud convert api key: "myapikeyabc123aoserhc"
```

For instructions on making a cloud convert API Key, you can visit [this page while logged in](https://cloudconvert.com/dashboard/api/v2/keys).

## Adding new Clauses

Once a clause is present in the Airtable data (see above), you can add its corresponding DOCX to the Google Drive folder, and it will be found and downloaded by this interview. It's important that the name of the DOCX in the Drive folder have the exact name of the clause somewhere in it, with the same spelling as in the Airtable. Otherwise, it won't be found and downloaded by this interview (ignoring `&` and `'`). For example, if the DOCX's name is "Gilbert _ Sullivan_s Clause - V3", and the Airtable "Child name" is "Gilbert & Sullivan's Clause", that's okay. But if the DOCX's name is "Chris_s Clause - V4" and the Airtable name is "Chris' Clause", it won't be found.

For some reason, the documents that we have been starting with have 10's to 100's of DOCX validation errors. These documents will generally open okay in Word or Google Docs on their own, but these validation errors cause problems when working with the open source libraries that we use to combine
the documents. We currently use cloud convert (converting from a DOCX file to an RTF file back to a DOCX file) to get rid of what seems to be most of the more serious errors, but the best way (and only way to
get rid of all of the errors that I've seen) is to use Microsoft Word's functionality for doing so. The process for doing that is recorded in the `windows_validation_converter.py` file. That file essentially does the below process, just automatically:

1. Download the document from Google Drive or other cloud editor and open locally with Desktop Word (works with Word 2019, but later versions probably should too).
2. Go to File > Save As, and save the file as a Rich Text Format (.rtf), and close Word.
3. Open the newly saved .rtf file in Word. Go to File > Save As, and now save as a Word Document (DOCX). Make sure that the "Maintain compatibility with previous versions of Word" is checked.
4. (optional) Sometimes, this process causes Word to make the background style of the tables in the document orange. To change this back to a normal white background, move your cursor into the table, and click on the "Design" tab above the ribbon. You should see the orange background in the "Table Styles". Delete it (right click > delete table style) from the document, and click on the desired table style. Save the document.
5. Upload the corrected DOCX files to the Google Drive folder that this interview is using.

## Authors

Bryce Willey, Quinten Steenhuis
