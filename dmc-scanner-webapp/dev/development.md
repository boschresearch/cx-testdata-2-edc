# minikube
```
minikube start
minikube dashboard
# opens the browser


alias kubectl="minikube kubectl --"

```

# Documentation
## md to pdf
```
sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-extra-utils texlive-latex-extra

pandoc LabelFields.md -o LabelFields.pdf
```

## pdf to png
Bad quality unfortunatelly.
```
sudo apt-get install imagemagick
convert LabelFields.pdf LabelFields.png

```