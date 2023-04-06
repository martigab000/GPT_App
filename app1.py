from website import create_app
#from .website import code, construct_index
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
