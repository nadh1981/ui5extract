Developed this python script to extract the details of UI5 artifacts to a document.

This is not part of any project delivery and I was learning python when writing this program. So this code is not optimized and may not align with any standards or best practices.

To get this working place the source code of projects you want to generate documents on into a root folder as below:
-  Root Folder 
    - Project 1
      - Component.js
      - index.html
      - .
      - ..
    - Project 1
      - Component.js
      - index.html
      - .
      - ..
                  
Update below line to with path to source folder in generatedocuments.py:
> Line 11: location = '' #should contain path to the source dir
