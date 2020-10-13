def generate_emails(first_name, last_name, domain):
    # Split name by whitescpaces. This is requred because we need to know if the name contains a middle name.
    name_in_a_list = [first_name, last_name]

    # if the name length is 2, that means there is no middle name here. Just firstname and lastname
    if len(name_in_a_list) == 2:
        first_name = name_in_a_list[0].lower()
        first_initial = first_name[0]
        last_name = name_in_a_list[1].lower()
        last_initial = last_name[0]
    else:
        first_name = name_in_a_list[0].lower()
        first_initial = first_name[0]
        middle_name = name_in_a_list[1].lower()
        middle_initial = middle_name[0]
        last_name = name_in_a_list[2].lower()
        last_initial = last_name[0]

    return [
        first_name + '@' + domain,
        last_name + '@' + domain,
        first_name + last_name + '@' + domain,
        first_name + '.' + last_name + '@' + domain,
        first_initial + last_name + '@' + domain,
        first_initial + '.' + last_name + '@' + domain,
        first_name + last_initial + '@' + domain,
        first_name + '.' + last_initial + '@' + domain,
        first_initial + last_initial + '@' + domain,
        first_initial + '.' + last_initial + '@' + domain,
        # last_name + first_name + '@' + domain,
        # last_name + '.' + first_name + '@' + domain,
        # last_name + first_initial + '@' + domain,
        # last_name + '.' + first_initial + '@' + domain,
        # last_initial + first_name + '@' + domain,
        # last_initial + '.' + first_name + '@' + domain,
        # last_initial + first_initial + '@' + domain,
        # last_initial + '.' + first_initial + '@' + domain,
        # first_initial + middle_initial + last_name + '@' + domain,
        # first_initial + middle_initial + '.' + last_name + '@' + domain,
        # first_name + middle_initial + last_name + '@' + domain,
        # first_name + '.' + middle_initial + '.' + last_name + '@' + domain,
        # first_name + middle_name + last_name + '@' + domain,
        # first_name + '.' + middle_name + '.' + last_name + '@' + domain,
        # first_name + '-' + last_name + '@' + domain,
        # first_initial + '-' + last_name + '@' + domain,
        # first_name + '-' + last_initial + '@' + domain,
        # first_initial + '-' + last_initial + '@' + domain,
        # last_name + '-' + first_name + '@' + domain,
        # last_name + '-' + first_initial + '@' + domain,
        # last_initial + '-' + first_name + '@' + domain,
        # last_initial + '-' + first_initial + '@' + domain,
        # first_initial + middle_initial + '-' + last_name + '@' + domain,
        # first_name + '-' + middle_initial + '-' + last_name + '@' + domain,
        # first_name + '-' + middle_name + '-' + last_name + '@' + domain,
        # first_name + '_' + last_name + '@' + domain,
        # first_initial + '_' + last_name + '@' + domain,
        # first_name + '_' + last_initial + '@' + domain,
        # first_initial + '_' + last_initial + '@' + domain,
        # last_name + '_' + first_name + '@' + domain,
        # last_name + '_' + first_initial + '@' + domain,
        # last_initial + '_' + first_name + '@' + domain,
        # last_initial + '_' + first_initial + '@' + domain,
        # first_initial + middle_initial + '_' + last_name + '@' + domain,
        # first_name + '_' + middle_initial + '_' + last_name + '@' + domain,
        # first_name + '_' + middle_name + '_' + last_name + '@' + domain,
    ]
