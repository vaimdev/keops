from xml.etree import cElementTree as ElementTree

xml = """
<form type="form">
    <field name="field1" />
    <group name="test">
        <field name="field2" />
    </group>
</form>
"""

el = ElementTree.fromstring(xml)
print(el)
for n in el:
    n.set('mynewattr', "1")
    print(ElementTree.tostring(n))
