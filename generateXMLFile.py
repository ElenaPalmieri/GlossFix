import json
import os

has_sub_elements = {
    'intro': ['jud', 'njud', 'nreg', 'judoff', 'court', 'obj', 'abs'],
    'court': ['J'],
    'partreq': ['req', 'claim', 'arg'],
    'courtmot': ['mot', 'find'],
    'courtdec': ['dec', 'cost', 'timestamp', 'subscr', 'place', 'date'],
    'timestamp': ['place', 'date']
}


needs_id = ['prem', 'conc', 'judge', 'prelitdec', 'req', 'claim', 'arg', 'mot', 'find', 'dec', 'subscr']


optional_attributes = {
    'judge': ['R'],
    'prelitdec': ['E'],
    'part': ['TP', 'PRO'],
    'claim': ['PRO', 'CON'],
    'arg': ['PRO', 'CON'],
    'prem': ['SUP', 'SFF', 'ATT', 'INH', 'REPH', 'S']
}


gloss_xml_dict = {
    'judgment': 'jud',
    'numberJudgment': 'njud',
    'numberRegister': 'nreg',
    'judicialOffice': 'judoff',
    'object': 'obj',
    'abstract': 'abs',
    'fact': 'fact',
    'place': 'place',
    'date': 'date',
    'intro': 'intro',
    'court': 'court',
    'courtMotivation': 'courtmot',
    'courtDecision': 'courtdec',
    'timestamp': 'timestamp',
    'judge': 'judge',
    'proceeding': 'proc',
    'prelitigationDecision': 'prelitdec',
    'party': 'part',
    'partyRequest': 'partreq',
    'request': 'req',
    'claim': 'claim',
    'argument': 'arg',
    'motivation': 'mot',
    'finding': 'find',
    'decision': 'dec',
    'litigationCosts': 'cost',
    'subscription': 'subscr',
    'premise': 'prem',
    'conclusion': 'conc'
}


attributes_dict = {
    'composition': 'C',
    'role': 'R',
    'instance': 'G',
    'outcome': 'E',
    'party': 'P',
    'is_third_party': 'TP',
    'pro': 'PRO',
    'proreq': 'PRO',
    'conreq': 'CON',
    'proclaim': 'PRO',
    'conclaim': 'CON',
    'object_claim': 'O',
    'object_request': 'O',
    'implies_decision': 'I',
    'implies_finding': 'I',
    'derives': 'D',
    'derives_motivation': 'D',
    'derives_finding': 'D',
    'judge': 'J',
    'supported by': 'SUP',
    'attacked by': 'ATT',
    'argumentation scheme': 'S',
    'inhibited by': 'INH',
    'supported from failure': 'SFF',
    'rephrased by': 'REPH',
    'type': 'T'
}


values_dict = {
    'Precedent': 'Prec',
    'Interpretative': 'Itpr',
    'Verbal classification': 'Class',
    'Authoritative': 'Aut',
    'Intention of the legislator': 'Psy',
    'Teleological': 'Tele',
    'Literal interpretation': 'Lit',
    'Systematic interpretation': 'Syst',
    'Principle': 'Princ',
    'Legal': 'L',
    'Factual': 'F',
    'LegalFactual': 'L|F',
    'Mono': 'Mono',
    'Collegiate': 'Coll',
    'Simple': 'Simple',
    'Grand': 'Grand',
    'Yes': '1',
    'No': '0',
    'President': 'Pres',
    'Rapporteur': 'Rapp',
    'DraftingJudge': 'Draft',
    'SimpleJudge': 'Judge',
    '1': '1',
    '2': '2',
    'REJECT': '0',
    'UPHOLD': '1',
    'INADMISSIBLE': '-1'
}


tag_counter = {
    'judgment': 0,
    'numberJudgment': 0,
    'numberRegister': 0,
    'judicialOffice': 0,
    'object': 0,
    'abstract': 0,
    'fact': 0,
    'place': 0,
    'date': 0,
    'intro': 0,
    'court': 0,
    'courtMotivation': 0,
    'courtDecision': 0,
    'timestamp': 0,
    'judge': 0,
    'proceeding': 0,
    'prelitigationDecision': 0,
    'partyRequest': 0,
    'request': 0,
    'claim': 0,
    'argument': 0,
    'motivation': 0,
    'finding': 0,
    'decision': 0,
    'litigationCosts': 0,
    'subscription': 0,
    'premise': 0,
    'conclusion': 0,
    'party': 'A'
}


id_correspondencies = {}

duplicates = [' D=', ' O=', ' I=']


# In Gloss we had to split some attributes based on the type they referred to
# For example, in the motivation tag ("mot"), object ("O") had to be splitted in OBJECT_REQUEST and OBJECT_CLAIM
# This function takes in input a tag like '<[...] O="Req1|Req2", O="Claim1|Claim2" [...]>'
# and turns it into '<[...] O="Req1|Req2|Claim1|Claim2" [...]>'
def aggregate_attributes(tags):
    result = []
    for tag in tags:
        for attribute in duplicates:
            if tag['text'].count(attribute) > 1:
                new_text = ''
                splits = tag['text'].split()
                for split in splits:
                    if attribute[1:] in split:
                        if attribute in new_text:
                            new_text = new_text + split.split('"')[1] + '"'
                        else:
                            new_text = new_text + attribute[1:] + '"' + split.split('"')[1] + '|'
                        if split.split('"')[2] == '>':
                            new_text = new_text + '>'
                        else:
                            if new_text[-1] != '|':
                                new_text = new_text + ' '
                    else:
                        if '>' in split:
                            new_text = new_text + split
                        else:
                            new_text = new_text + split + ' '

                tag['text'] = new_text
                tag['len'] = len(new_text)
        result.append(tag)
    return result


# The references to other tags are obtained trough IDs, this function substitutes the Gloss ID with the correspondent
# XML one usind the id_correspondencies dictionary (that has Gloss IDs for keys and the correspondent XML ones as values)
def sort_tag_references(tags):
    result = []
    for tag in tags:
        for key in id_correspondencies.keys():
            if key in tag['text']:
                tag['pos'] = tag['pos']
                if type(id_correspondencies[key]) is tuple:
                    tag['text'] = tag['text'].replace(key, id_correspondencies[key][0])
                else:
                    tag['text'] = tag['text'].replace(key, id_correspondencies[key])
                tag['len'] = len(tag['text'])
        result.append(tag)
    return result


# In Gloss the names of the attributes are complete and therefore longer, the XML names are shorter
# The attributes_dict dictionary contains the correspondencies
def get_xml_attribute(gloss_name):
    if gloss_name.lower() in attributes_dict.keys():
        return attributes_dict[gloss_name.lower()]
    elif gloss_name in gloss_xml_dict.keys():
        return gloss_xml_dict[gloss_name]
    else:
        print('ERROR, ATTRIBUTE NAME NOT FOUND -> ' + gloss_name)


# Returns the same name but with the first letter in upper case
def make_first_cap(name):
    return name[0].upper() + name[1:]


# Called every time the analysis of a new document starts, resets the counters used to make the IDs of the tags
def reset_tag_counter():
    for key in tag_counter.keys():
        if key == 'party':
            tag_counter[key] = 'A'
        else:
            tag_counter[key] = 0


# Sorting funcion for ordering tags based on their twin's position
# (each tag is split into two, the opening <tag> and the closure </tag>)
def sort_by_twin(e):
    return e['twin_tag_pos']


# Sorting function based on the order attribute
def sort_by_order(e):
    return e['order']


# Sorting function based on the beginning of the tag
def sort_by_pos(e):
    return e['pos']


# The tags that start at the same position should be ordered based on the position of the thir closure and vicecersa
# Also, the tags that begin and end in the same position should follow the correct order for the closure
def sort_tags_by_precedence(tags):
    order = 0
    for i in range(0, len(tags)):
        if 'order' not in tags[i].keys():
            start_tags = []
            end_tags = []
            for tag in tags:
                if tag['pos'] == tags[i]['pos']:
                    if tag['start_tag']:
                        start_tags.append(tag)
                    else:
                        end_tags.append(tag)

            if len(end_tags) > 1:
                end_tags.sort(key=sort_by_twin)
                end_tags.reverse()
                for t in end_tags:
                    t['order'] = order
                    order += 1
            elif end_tags:
                end_tags[0]['order'] = order
                order += 1

            if len(start_tags) > 1:
                start_tags.sort(key=sort_by_twin)
                start_tags.reverse()
                for t in start_tags:
                    t['order'] = order
                    order += 1
            elif start_tags:
                start_tags[0]['order'] = order
                order += 1

    for i in range(0, len(tags)):
        same_end_pos = []
        if not tags[i]['sorted'] and not tags[i]['start_tag']:
            tags[i]['sorted'] = True
            for tag in tags:
                if tag != tags[i] and tag['pos'] == tags[i]['pos'] and tag['twin_tag_pos'] == tags[i]['twin_tag_pos'] and not tag['start_tag']:
                    same_end_pos.append(tag)
                    tag['sorted'] = True
            if len(same_end_pos) > 0:
                same_end_pos.append(tags[i])
                order_numbers = []
                for tag in same_end_pos:
                    order_numbers.append(tag['order'])
                order_numbers.reverse()
                for j in range(0, len(same_end_pos)):
                    same_end_pos[j]['order'] = order_numbers[j]


    tags.sort(key=sort_by_order)
    return tags


# Finds the Gloss name of the attribute, given its Gloss ID
def find_name(datastore, type_id):
    for t in datastore['types']:
        if t['_id'] == type_id:
            return t['name']
    print('ERROR: tag name not found for id: ' + type_id)
    return False


# Returns the list of attributes of a given tag (takes it from the description of the types)
def get_attribute_list(datastore, tag_name):
    attributes = []
    count = 0

    index = -1
    for tag in datastore['types']:
        if tag['name'] == tag_name:
            index = count
            break
        count = count + 1

    for attribute in datastore['types'][index]['attributes']:
        attributes.append(attribute['name'])

    return attributes


# Removes the sub-elements that in Gloss are indicated as attributes, while in XML are not indicated in the tag
# In XML, they are just a sub-tree of the tag
def remove_sub_elements(text, name):
    new_text = ''
    current_attribute = ''
    for split in text.split(' '):
        if '=' not in split and '<' not in split:
            if current_attribute not in has_sub_elements[name]:
                new_text = new_text + split + ' '
        else:
            current_attribute = split.split('=')[0]
            if split.split('=')[0] not in has_sub_elements[name]:
                if '<' not in split:
                    new_text = new_text + ' '
                new_text = new_text + split
    if new_text[-1] != '>':
        new_text = new_text + '>'
    return new_text


# Removes the attributes that have no value, but only if they are optional
def remove_non_set_attributes(text, name):
    result = ''
    text = text[1:-1]
    for attribute in text.split(' '):
        if not ((attribute.split('=')[0] in optional_attributes[name] and ('[None]' in attribute.split('=')[1] or 'not' in attribute.split('=')[1]))
                or ('set--' in attribute and (name == 'prelitdec' or name == 'prem'))):
            result = result + attribute + ' '
    result = '<' + result[:-1] + '>'
    return result


# Creates the text of the XML tag
def create_tag_text(datastore, tag, type):
    text = ''
    # Opening of the tag
    if type == 'start':
        text = text + '<'
    elif type == 'end':
        text = text + '</'
    else:
        print('ERROR: Tag type not recognized')
        return False

    gloss_name = find_name(datastore, tag['type'])
    xml_name = gloss_xml_dict[gloss_name]
    text = text + xml_name

    # Tag attributes
    if type == 'start':

        # ID
        if gloss_name == 'party':
            text = text + ' '
            id_correspondencies[tag['_id']] = tag_counter['party'],
            text = text + 'P="' + tag_counter['party'] + '"'
            tag_counter['party'] = chr(ord(tag_counter['party']) + 1)
        # Changing this in a normal else will result in having the ID for every tag
        elif xml_name in needs_id:
            text = text + ' '
            tag_number = tag_counter[gloss_name] + 1
            tag_counter[gloss_name] = tag_counter[gloss_name] + 1
            xml_id = make_first_cap(xml_name) + str(tag_number)
            # Save the original ID for dependencies in attributes
            id_correspondencies[tag['_id']] = xml_id
            text = text + 'ID="' + xml_id + '"'

        attribute_list = get_attribute_list(datastore, gloss_name)

        for i in range(0, len(attribute_list)):
            if tag['attributes'][i]['value']:
                if isinstance(tag['attributes'][i]['value'], list) and tag['attributes'][i]['value'][0]:
                    text = text + ' ' + get_xml_attribute(attribute_list[i]) + '="'
                    for j in range(0, len(tag['attributes'][i]['value'])):
                        if tag['attributes'][i]['value'][j] in values_dict.keys():
                            text = text + values_dict[tag['attributes'][i]['value'][j]]
                        else:
                            text = text + tag['attributes'][i]['value'][j]
                        if j < len(tag['attributes'][i]['value'])-1:
                            text = text + '|'
                    text = text + '"'
                else:
                    if str(tag['attributes'][i]['value']) in values_dict.keys():
                        print(get_xml_attribute(attribute_list[i]))
                        print(values_dict[str(tag['attributes'][i]['value'])])
                        text = text + ' ' + get_xml_attribute(attribute_list[i]) + '="' + values_dict[str(tag['attributes'][i]['value'])] + '"'
                    else:
                        text = text + ' ' + get_xml_attribute(attribute_list[i]) + '="' + str(tag['attributes'][i]['value']) + '"'


    # Closure of the tag
    text = text + '>'

    # Removing parts of the tags (Doing it after the creation of the tag just in case we want them back in the future)

    # Removing sub-elements
    if xml_name in has_sub_elements.keys():
        text = remove_sub_elements(text, xml_name)

    # Removing the third party attribute if the party is not a third party
    if 'TP=0' in text:
        text.replace(' TP=0', '')

    # Removing non-set optional attributes
    if xml_name in optional_attributes.keys():
        text = remove_non_set_attributes(text, xml_name)

    return text


def generate_xml_file(filename):

    try:
        os.mkdir('.\\xml_files')
    except OSError:
        print("Creation of the directory %s failed" % path)

    with open(filename, 'r', encoding='utf8') as f:
        datastore = json.load(f)

    # Crating different copies of the same document for the different annotators
    for document in datastore['documents']:
        annotators = []
        for annotation in datastore['annotations']:
            if annotation['document'] == document['_id'] and annotation['owner'] not in annotators:
                annotators.append(annotation['owner'])
        if len(annotators) > 1:
            for i in range(1, len(annotators)):
                document_copy = {}
                document_copy['name'] = document['name'].split('.')[0] + str(i) + '.txt'
                document_copy['plainText'] = document['plainText']
                new_document_id = document['_id'] + str(i)
                document_copy['_id'] = new_document_id
                datastore['documents'].append(document_copy)
                for annotation in datastore['annotations']:
                    if annotation['document'] == document['_id'] and annotation['owner'] == annotators[i]:
                        annotation['document'] = new_document_id

    for document in datastore['documents']:

        reset_tag_counter()

        # The internal id is used to match the opening and the closure of the same tag
        internal_tag_id = 0

        # The file name will be the document name
        name = str(document['name'])
        file_name = '.\\xml_files\\' + name.split('.')[0] + '.xml'

        xml_file = open(file_name, 'w', encoding='utf8')

        # Getting the plain text of the document from the JSON file
        text = document['plainText']

        # Creation of the XML tags for the document
        tags = []
        for tag in datastore['annotations']:
            # The 'annotations' object contains all the annotations of the task, i.e. of all the documents
            if tag['document'] == document['_id']:
                # Two different tags are generated:
                # tag_start represents the opening of the XML tag (e.g. <judge ID="Judge3" R="Judge">)
                # tag_end represents the closure of the XML tag (e.g. </judge>)
                start_text = create_tag_text(datastore, tag, 'start')
                tag_start = {'pos': tag['start'],
                             'text': start_text,
                             'len': len(start_text),
                             'internal_id': internal_tag_id,
                             'start_tag': True,
                             'twin_tag_pos': tag['end'],
                             'sorted': False}
                tags.append(tag_start)
                end_text = create_tag_text(datastore, tag, 'end')
                tag_end = {'pos': tag['end'],
                           'text': end_text,
                           'len': len(end_text),
                           'internal_id': internal_tag_id,
                           'start_tag': False,
                           'twin_tag_pos': tag['start'],
                           'sorted': False}
                tags.append(tag_end)
                internal_tag_id += 1

        tags = sort_tag_references(tags)
        tags = aggregate_attributes(tags)

        tags.sort(key=sort_by_pos)

        tags = sort_tags_by_precedence(tags)
        
        # The count variable keeps track of the offset created by the length of the XML tags that are already in the text
        # This makes it possible to write the following tags in the correct position
        count = 0
        for tag in tags:
            text = text[:count+tag['pos']] + tag['text'] + text[count+tag['pos']:]
            count = count + tag['len']

        xml_file.write(text)
        xml_file.close()

    f.close()
