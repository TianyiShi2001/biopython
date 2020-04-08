from urllib import request


class _SeqDb(object):
    name = ""
    base_url = ""
    entry_url = ""  # to be formatted; e.g. http://www.rcsb.org/structure/{} ; defaults to base_url + "/" + id
    fetch_url = ""
    fetch_file_format_map = dict(fasta="fasta", genbank="genbank")
    fetch_file_format_default = "genbank"

    @classmethod
    def make_identifier(cls, id_obj):
        return id_obj.id

    @classmethod
    def make_entry_url(cls, id_obj):
        identifier = cls.make_identifier(id_obj)
        if cls.entry_url:
            return cls.entry_url.format(identifier)
        return cls.base_url + "/" + str(identifier)

    @classmethod
    def fetch(cls, accession_code, file_format=None):
        if not cls.fetch_url:
            raise Exception("This database does not support fetching!")
        if not file_format:
            file_format = cls.fetch_file_format_default
        fmt = cls.fetch_file_format_map.get(file_format)
        if not fmt:
            raise Exception(
                f"""Cannot fetch the format {file_format} from this database!
available formats: "{'", "'.join(cls.fetch_file_format_map.keys())}" """
            )
        url = cls.fetch_url.format(
            id=accession_code, format=cls.fetch_file_format_map[file_format],
        )
        return request.urlopen(url).read().decode("utf8")
