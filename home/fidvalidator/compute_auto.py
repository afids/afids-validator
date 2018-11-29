import numpy as np
import os

def compute_mean_std(filename=None):
    data = np.loadtxt(os.path.join('uploads', filename))
    return """
Data from file <tt>%s</tt>:
<p>
<table border=1>
<tr><td> infracollicular sulcus    </td><td> %.3g </td></tr>
<tr><td> PMJ </td><td> %.3g </td></tr>
<tr><td> superior interpeduncular fossa </td><td> %.3g </td></tr>
<tr><td> R superior LMS </td><td> %.3g </td></tr>
<tr><td> L superior LMS </td><td> %.3g </td></tr>
<tr><td> R inferior LMS </td><td> %.3g </td></tr>
<tr><td> L superior LMS </td><td> %.3g </td></tr>
<tr><td> L inferior LMS </td><td> %.3g </td></tr>
<tr><td> Culmen </td><td> %.3g </td></tr>
<tr><td> Intermamillary sulcus </td><td> %.3g </td></tr>
<tr><td> R MB </td><td> %.3g </td></tr>
<tr><td> L MB </td><td> %.3g </td></tr>
<tr><td> pineal gland </td><td> %.3g </td></tr>
<tr><td> R LV at AC </td><td> %.3g </td></tr>
<tr><td> L LV at AC </td><td> %.3g </td></tr>
<tr><td> R LV at PC </td><td> %.3g </td></tr>
<tr><td> L LV at PC </td><td> %.3g </td></tr>
<tr><td> Genu of CC </td><td> %.3g </td></tr>
<tr><td> Splenium of CC </td><td> %.3g </td></tr>
<tr><td> L AL temporal horn </td><td> %.3g </td></tr>
<tr><td> L superior AM temporal horn </td><td> %.3g </td></tr>
<tr><td> R inferior AM temporal horn </td><td> %.3g </td></tr>
<tr><td> L inferior AM temporal horn </td><td> %.3g </td></tr>
<tr><td> R indusium griseum origin </td><td> %.3g </td></tr>
<tr><td> L indisium griseum origin </td><td> %.3g </td></tr>
<tr><td> R ventral occipital horn </td><td> %.3g </td></tr>
<tr><td> L ventral occipital horn </td><td> %.3g </td></tr>
<tr><td> R olfactory sulcul fundus </td><td> %.3g </td></tr>
<tr><td> L olfactory sulcul fundus </td><td> %.3g </td></tr>


""" % (filename, np.mean(data), np.std(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), 
	np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), 
	np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), np.mean(data), 
	np.mean(data), np.mean(data), np.mean(data), np.mean(data))
