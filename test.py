deadLinks = [(1,2)]
print deadLinks
deadLinks = [(name, ip) for name, ip in deadLinks if ip != 1 and name != 1]
print deadLinks