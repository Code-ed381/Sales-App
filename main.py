import sqlite3
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from PyQt6.uic import loadUi
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

database_path = './database/'
filename = 'database'

isExist = os.path.exists(database_path)

if isExist == True:
    pass
else:
    os.makedirs(database_path, exist_ok=True)
    db = sqlite3.connect(database_path + filename + '.sqlite3')

    db.execute("""CREATE TABLE "cart" (
        "CartID"	INTEGER,
        "ProductID"	INTEGER NOT NULL,
        "Quantity"	INTEGER NOT NULL,
        FOREIGN KEY("ProductID") REFERENCES "product"("ProductID"),
        PRIMARY KEY("CartID" AUTOINCREMENT)
    );""")
    db.execute("""CREATE TABLE "category" (
        "CategoryID"	INTEGER NOT NULL,
        "CategoryName"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("CategoryID")
    );""")
    db.execute("""CREATE TABLE "product" (
        "ProductID"	INTEGER NOT NULL,
        "ProductName"	TEXT NOT NULL UNIQUE,
        "Description"	TEXT NOT NULL,
        "Quantity"	INTEGER NOT NULL,
        "Price"	INTEGER NOT NULL,
        "CategoryID"	INTEGER,
        FOREIGN KEY("CategoryID") REFERENCES "category"("CategoryID"),
        PRIMARY KEY("ProductID")
    );""")
    db.execute("""CREATE TABLE "customer" (
        "CustomerID"	INTEGER NOT NULL,
        "CustomerName"	TEXT NOT NULL,
        "Phone"	TEXT NOT NULL,
        "Email"	TEXT NOT NULL,
        "BusinessName"	TEXT NOT NULL,
        PRIMARY KEY("CustomerID")
    );""")
    db.execute("""CREATE TABLE "purchase" (
        "PurchaseID"	INTEGER,
        "Items"	TEXT NOT NULL,
        "Total_Amount"	INTEGER NOT NULL,
        "Amount_Paid"	INTEGER NOT NULL,
        "Balance"	INTEGER NOT NULL,
        "DateTime"	TEXT NOT NULL,
        PRIMARY KEY("PurchaseID" AUTOINCREMENT)
    );""")
    db.execute("""CREATE TABLE "users" (
        "id"	INTEGER NOT NULL,
        "username"	TEXT NOT NULL,
        "name"	TEXT NOT NULL,
        "email"	TEXT NOT NULL,
        "password"	TEXT NOT NULL UNIQUE,
        "image"	TEXT NOT NULL,
        "role"	INTEGER NOT NULL DEFAULT 'admin',
        PRIMARY KEY("id" AUTOINCREMENT)
    );""")
    db.execute("""CREATE TABLE "supplier" (
        "SupplierID"	INTEGER,
        "SupplierName"	TEXT NOT NULL,
        "Phone"	INTEGER NOT NULL,
        "Email"	TEXT NOT NULL,
        PRIMARY KEY("SupplierID" AUTOINCREMENT)
    );""")
    db.execute("""CREATE TABLE "report" (
        "ReportID"	INTEGER,
        "Item"	TEXT,
        "Quantity"	INTEGER NOT NULL,
        "DateTime"	TEXT NOT NULL,
        PRIMARY KEY("ReportID" AUTOINCREMENT)
    );""")

    db.commit()

db = sqlite3.connect(database_path + filename + '.sqlite3')
mycursor = db.cursor()

users = mycursor.execute("SELECT * FROM users").fetchall()


#######START - PUBLIC########
class AddProduct(QDialog):
    def __init__(self, table, deleteClicked):
        super(AddProduct, self).__init__()
        loadUi('./UIs/add_product.ui', self)
        self.save.clicked.connect(self.addNewProduct)

        try:
            rows = mycursor.execute("SELECT * FROM category").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error occurred',
                'Get Categories Failed',
                QMessageBox.StandardButton.Ok
            )
        
        self.table = table
        self.deleteClicked = deleteClicked
        self.cancel.clicked.connect(self.closeIt)

        self.description.setPlaceholderText('Product description')
        self.name.setPlaceholderText('Name')
        self.price.setPlaceholderText('Price')
        self.quantity.setPlaceholderText('Quantity')
        self.category.setPlaceholderText("--Choose Category--")
        
        for item in rows:
            self.category.addItem(item[1])


    def closeIt(self): 
        self.close()

    def addNewProduct(self):
        try:
            product_name = self.name.text()
            price = self.price.text()
            quantity = self.quantity.text()
            description = self.description.toPlainText()
            category = self.category.currentIndex()

            try: 
                query = """INSERT INTO product (ProductName, Description, Quantity, Price, CategoryID) VALUES(?,?,?,?,?)"""
                data = (product_name, description, quantity, price, category + 1)
                mycursor.execute(query, data)
                db.commit()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error occurred',
                    'Insert Product Failed',
                    QMessageBox.StandardButton.Ok
                )

            try:
                query = "SELECT CategoryName FROM category WHERE CategoryID = ?"
                cat = mycursor.execute(query, (category+1,)).fetchone()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error occurred',
                    'Select From Category Failed',
                    QMessageBox.StandardButton.Ok
                )

            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)

            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)

            self.table.setItem(rowPosition, 0, QTableWidgetItem('#'))
            self.table.setItem(rowPosition, 1, QTableWidgetItem(product_name))
            self.table.setItem(rowPosition, 2, QTableWidgetItem(description))
            self.table.setItem(rowPosition, 3, QTableWidgetItem(str(quantity)))
            self.table.setItem(rowPosition, 4, QTableWidgetItem(str(price)))
            self.table.setItem(rowPosition, 5, QTableWidgetItem(str(cat[0])))
            self.table.setCellWidget(rowPosition, 6, self.delete_btn)

            self.close()

            QMessageBox.information(
                self,
                'Successful',
                'Product Added successfully',
                QMessageBox.StandardButton.Ok
            )

        except:
            QMessageBox.critical(
                self,
                'Error',
                'Fill out all fields',
                QMessageBox.StandardButton.Ok
            )
class AddCustomer(QDialog):
    def __init__(self, customer_table, deleteClicked):
        super(AddCustomer, self).__init__()
        loadUi('./UIs/add_customer.ui', self)
        self.save.clicked.connect(self.addNewCustomer)
        self.cancel.clicked.connect(self.closeIt)   
        self.customer_table = customer_table
        self.deleteClicked = deleteClicked

    def closeIt(self): 
        self.close()

    def addNewCustomer(self):
        name = self.name.text()
        phone = self.phone.text()
        email = self.email.text()
        business = self.bisiness.toPlainText()

        try:
            query = """INSERT INTO customer (CustomerName, Phone, Email, BusinessName) VALUES(?,?,?,?)"""
            data = (name, phone, email, business)
            mycursor.execute(query, data)
            db.commit()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error occurred',
                'Add Customer Failed!',
                QMessageBox.StandardButton.Ok
            )

        self.delete_btn = QPushButton('delete')
        self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
        self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
        self.delete_btn.clicked.connect(self.deleteClicked)

        rowPosition = self.customer_table.rowCount()
        self.customer_table.insertRow(rowPosition)

        self.customer_table.setItem(rowPosition, 0, QTableWidgetItem(str(name)))
        self.customer_table.setItem(rowPosition, 1, QTableWidgetItem(str(phone)))
        self.customer_table.setItem(rowPosition, 2, QTableWidgetItem(str(email)))
        self.customer_table.setItem(rowPosition, 3, QTableWidgetItem(str(business)))
        self.customer_table.setCellWidget(rowPosition, 4, self.delete_btn)
        
        self.close()

        QMessageBox.information(
            self,
            'Successful',
            'Customer added',
            QMessageBox.StandardButton.Ok
        )
class AddSupplier(QDialog):
    def __init__(self, customer_table, deleteClicked):
        super(AddSupplier, self).__init__()
        loadUi('./UIs/add_supplier.ui', self)
        self.save.clicked.connect(self.addNewCustomer)
        self.cancel.clicked.connect(self.closeIt)   
        self.customer_table = customer_table
        self.deleteClicked = deleteClicked

    def closeIt(self): 
        self.close()

    def addNewCustomer(self):
        name = self.name.text()
        phone = self.phone.text()
        email = self.email.text()

        try:
            query = """INSERT INTO supplier (SupplierName, Phone, Email) VALUES(?,?,?)"""
            data = (name, phone, email)
            mycursor.execute(query, data)
            db.commit()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error occurred',
                'Add Supplier Failed!',
                QMessageBox.StandardButton.Ok
            )

        self.delete_btn = QPushButton('delete')
        self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
        self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
        self.delete_btn.clicked.connect(self.deleteClicked)

        rowPosition = self.customer_table.rowCount()
        self.customer_table.insertRow(rowPosition)

        self.customer_table.setItem(rowPosition, 0, QTableWidgetItem(str(name)))
        self.customer_table.setItem(rowPosition, 1, QTableWidgetItem(str(phone)))
        self.customer_table.setItem(rowPosition, 2, QTableWidgetItem(str(email)))
        self.customer_table.setCellWidget(rowPosition, 3, self.delete_btn)
        
        self.close()

        QMessageBox.information(
            self,
            'Successful',
            'Supplier added',
            QMessageBox.StandardButton.Ok
        )
class AddUser(QDialog):
    def __init__(self, users_table, deleteClicked):
        super(AddUser, self).__init__()
        loadUi('./UIs/add_user.ui', self)
        self.save.clicked.connect(self.addNewUser)
        self.cancel.clicked.connect(self.closeIt) 
        self.upload_btn.clicked.connect(self.uploadFile)
        self.users_table = users_table
        self.deleteClicked = deleteClicked

        self.role.setPlaceholderText("--Choose Role--")

        for role in ("Sales Attendant", "Store Officer", "Admin"):
            self.role.addItem(role)

    def closeIt(self): 
        self.close()

    def uploadFile(self):
        self.img = QFileDialog.getOpenFileName(self, "Upload Image", 'c:/', "Image files(*.jpg *png)")
        self.profile_image.setText(self.img[0])

    def addNewUser(self):
        fullname = self.fullname.text()
        username = self.username.text()
        email = self.email.text()
        password = self.password.text()
        user_role = self.role.currentIndex()

        if user_role == 0:
            try:
                query = """INSERT INTO users (username, name, email, password, image, role) VALUES(?,?,?,?,?,?)"""
                data = (username, fullname, email, password,self.img[0], 'sales')
                mycursor.execute(query, data)
                db.commit()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error occurred',
                    'Add Customer Failed!',
                    QMessageBox.StandardButton.Ok
                )
        elif user_role == 1:
            try:
                query = """INSERT INTO users (username, name, email, password, image, role) VALUES(?,?,?,?,?,?)"""
                data = (username, fullname, email, password,self.img[0], 'store')
                mycursor.execute(query, data)
                db.commit()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error occurred',
                    'Add Customer Failed!',
                    QMessageBox.StandardButton.Ok
                )
        elif user_role == 2:
            try:
                query = """INSERT INTO users (username, name, email, password, image, role) VALUES(?,?,?,?,?,?)"""
                data = (username, fullname, email, password,self.img[0], 'admin')
                mycursor.execute(query, data)
                db.commit()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error occurred',
                    'Add Customer Failed!',
                    QMessageBox.StandardButton.Ok
                )
        else:
            QMessageBox.critical(
                self,
                'Error',
                'No Role Selected',
                QMessageBox.StandardButton.Ok
            )


        self.delete_btn = QPushButton('delete')
        self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
        self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
        self.delete_btn.clicked.connect(self.deleteClicked)

        rowPosition = self.users_table.rowCount()
        self.users_table.insertRow(rowPosition)

        self.users_table.setItem(rowPosition, 0, QTableWidgetItem(str(fullname)))
        self.users_table.setItem(rowPosition, 1, QTableWidgetItem(str(username)))
        self.users_table.setItem(rowPosition, 2, QTableWidgetItem(str(email)))
        self.users_table.setItem(rowPosition, 3, QTableWidgetItem(str(password)))
        if user_role == 0:
            self.users_table.setItem(rowPosition, 4, QTableWidgetItem("sales attendant"))
        elif user_role == 1:
            self.users_table.setItem(rowPosition, 4, QTableWidgetItem("store officer"))
        elif user_role == 2:
            self.users_table.setItem(rowPosition, 4, QTableWidgetItem("admin"))
        self.users_table.setCellWidget(rowPosition, 5, self.delete_btn)
        
        self.close()

        QMessageBox.information(
            self,
            'Successful',
            'User added',
            QMessageBox.StandardButton.Ok
        )
class AddToCart(QDialog):
    def __init__(self, product_id):
        self.item = product_id
        # self.product_quantity = product_quantity
        super(AddToCart, self).__init__()
        loadUi('./UIs/add_to_cart.ui', self)

        self.quantity.setPlaceholderText('Enter quantity')
        self.cancel_2.clicked.connect(self.closeIt)
        self.add.clicked.connect(self.add_to_cart)

    def closeIt(self): 
        self.close()

    def add_to_cart(self):
        quantity = self.quantity.text()

        if int(quantity) <= int(product_quantity):
            try:
                query = "INSERT INTO cart (ProductID, Quantity) VALUES (?, ?)"
                mycursor.execute(query, (self.item,int(quantity)))
                db.commit()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error occurred',
                    'Add Product To Cart Failed!',
                    QMessageBox.StandardButton.Ok
                )

            QMessageBox.information(
                self,
                'Successful',
                'Added to cart',
                QMessageBox.StandardButton.Ok
            )
            self.close()
        else:
                QMessageBox.critical(
                self,
                'Quantity Error!',
                'The quantity you entered is more than we have in stock!',
                QMessageBox.StandardButton.Ok
            )
class Success(QDialog):
    def __init__(self):
        super(Success, self).__init__()
        loadUi('./UIs/success.ui', self)

        self.save.clicked.connect(self.closeIt)

    def closeIt(self): 
        self.close()
class AddCategory(QDialog):
    def __init__(self):
        super(AddCategory, self).__init__()
        loadUi('./UIs/add_category.ui', self)
        self.save.clicked.connect(self.addCategory)
        self.name.setPlaceholderText('Category name')
        self.cancel.clicked.connect(self.closeIt) 


    def addCategory(self):
        category_name = self.name.text()

        try:
            query = """INSERT INTO category (CategoryName) VALUES(?)"""
            mycursor.execute(query, (category_name,))
            db.commit()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error occurred',
                'Add Category Failed',
                QMessageBox.StandardButton.Ok
            )

        self.close();

        QMessageBox.information(
            self,
            'Successful',
            'Category Added',
            QMessageBox.StandardButton.Ok
        )



    def closeIt(self): 
        self.close()
class AmountPaid(QDialog):
    def __init__(self, cartItems, total):
        super(AmountPaid, self).__init__()
        loadUi('./UIs/amount_paid.ui', self)
        self.setWindowIcon(QIcon('./icons/icons8-stack-of-coins-96.png'))
        self.setWindowTitle("Amount Paid")
        self.cartItems = cartItems
        self.proceed.clicked.connect(self.make_purchase)
        self.cancel.clicked.connect(self.closeIt) 
        self.total = total

    def make_purchase(self):
        global amount
        amount = self.amount.text()
        # self.close()

        if int(amount) >= int(totals):
            if self.cartItems != []:
                # row = self.cart.currentRow()
                msgbox = QMessageBox()
                msgbox.setStyleSheet("QMessagebox {background-color: rgb(255, 255, 255);}")
                button = msgbox.question(
                    self,
                    'Purchase',
                    'Confirm Purchase',
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No
                )

                if button == QMessageBox.StandardButton.Yes:
                    items = ''
                    comma = ', '
                    print(self.cartItems)


                    for item in self.cartItems:
                        items += item[3]
                        items += comma
                        new_quantity = int(item[5]) - int(item[2])
                        try:
                            query = "UPDATE product SET Quantity = ? WHERE ProductID = ?"
                            mycursor.execute(query, (new_quantity, int(item[1])))
                            db.commit()
                        except:
                            QMessageBox.critical(
                                self,
                                'Failed - Database error occurred',
                                'Update Quantity Failed',
                                QMessageBox.StandardButton.Ok
                            )

                    for report in self.cartItems:
                        try:
                            query = "INSERT INTO report(Item, Quantity) VALUES (?,?,datetime('now'))"
                            mycursor.execute(query,(report[3], report[2]))
                            db.commit()
                        except:
                            QMessageBox.critical(
                                self,
                                'Failed - Database error occurred',
                                'Insert Report Failed',
                                QMessageBox.StandardButton.Ok
                            )


                    balance = self.total - int(amount)

                    try:
                        query = "INSERT INTO purchase(Items, Total_Amount, Amount_Paid, Balance,DateTime) VALUES (?,?,?,?,datetime('now'))"
                        mycursor.execute(query,(items,self.total,amount,balance))
                        db.commit()


                    except:
                        QMessageBox.critical(
                            self,
                            'Failed - Database error occurred',
                            'Record Purchase Failed',
                            QMessageBox.StandardButton.Ok
                        )

                    button = QMessageBox.information(
                        self,
                        'Successful',
                        'Items Purchased successfuly',
                        QMessageBox.StandardButton.Ok
                    )
                    if button == QMessageBox.StandardButton.Ok:
                        cartTable.clearContents()
                        try:
                            query = "DELETE FROM cart"
                            mycursor.execute(query)
                            db.commit()
                        except:
                            QMessageBox.critical(
                                self,
                                'Failed - Database error occurred',
                                'Clear Cart Failed',
                                QMessageBox.StandardButton.Ok
                            )

                        print("Cart cleared successfully")
                        cartAmount.setText(str(0))

                        self.close()
                        cartView.close()
            else:
                button = QMessageBox.information(
                    self,
                    'Empty cart',
                    'No Item In Cart',
                    QMessageBox.StandardButton.Ok
                )
                self.close()
        else:
            button = QMessageBox.information(
                self,
                'Amount!',
                'The amount you entered is less than the total amount',
                QMessageBox.StandardButton.Ok
            )


    def closeIt(self): 
        self.close()
class ViewCart(QDialog):
    def __init__(self):
        super(ViewCart, self).__init__()
        loadUi('./UIs/cart_view.ui', self)

        try:
            global cartItems
            cartItems = mycursor.execute("SELECT * FROM cart INNER JOIN product USING(ProductID)").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error occurred',
                'Select From Cart Failed',
                QMessageBox.StandardButton.Ok
            )

        unit = 0
        
        self.total = 0

        for row in cartItems:
            unit = row[6] * row[2]
            self.total += unit

        global totals
        totals = self.total

        self.amount.setText(str(self.total))
        self.purchase.clicked.connect(self.executeMakePurchase)
        self.clear.clicked.connect(self.clearCart)

        global cartTable
        global cartAmount
        global cartView 
        cartView = self
        cartTable = self.cart
        cartAmount = self.amount

        label = ['ID','Item', 'Quantity', 'Price', 'Delete']

        self.cart.setColumnCount(5)
        self.cart.setColumnWidth(0, 70)
        self.cart.setColumnWidth(1, 150)
        self.cart.setColumnWidth(2, 70)
        self.cart.setColumnWidth(3, 70)
        self.cart.setColumnWidth(4, 70)

        self.cart.setHorizontalHeaderLabels(label)
        self.cart.setRowCount(len(cartItems))

        row = 0
        for e in cartItems:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)

            self.cart.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.cart.setItem(row, 1, QTableWidgetItem(e[3]))
            self.cart.setItem(row, 2, QTableWidgetItem(str(e[2])))
            self.cart.setItem(row, 3, QTableWidgetItem(str(e[6])))
            self.cart.setCellWidget(row, 4, self.delete_btn)
            row += 1

    def executeMakePurchase(self):
        cart = mycursor.execute("SELECT * FROM cart INNER JOIN product USING(ProductID)").fetchall()
        if cart != []:
            paid = AmountPaid(cartItems, self.total)
            paid.exec()
        else:
            button = QMessageBox.information(
                self,
                'Empty cart',
                'No Item In Cart',
                QMessageBox.StandardButton.Ok
            )
            if button == QMessageBox.StandardButton.Ok:
                self.close()

    def purchases(self):
        if cartItems != []:
            row = self.cart.currentRow()

            button = QMessageBox.question(
                self,
                'Purchase',
                'Confirm Purchase',
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            )

            if button == QMessageBox.StandardButton.Yes:

                items = ''
                comma = ', '

                for item in cartItems:
                    items += item[3]
                    items += comma

                try:
                    query = "INSERT INTO purchase(Items, Total_Amount, Amount_Paid, DateTime) VALUES (?,?,?,datetime('now'))"
                    mycursor.execute(query,(items,self.total,amount))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error occurred',
                        'Purchase Record Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Items Purchased successfuly',
                    QMessageBox.StandardButton.Ok
                )
                if button == QMessageBox.StandardButton.Ok:
                    self.cart.clearContents()

                    try:
                        query = "DELETE FROM cart"
                        mycursor.execute(query)
                        db.commit()
                    except:
                        QMessageBox.critical(
                            self,
                            'Failed - Database error occurred',
                            'Cart Clear Failed',
                            QMessageBox.StandardButton.Ok
                        )

                    print("Cart cleared successfully")
                    self.amount.setText(str(0))

                    self.close()
        else:
            button = QMessageBox.information(
                self,
                'Empty cart',
                'No Item In Cart',
                QMessageBox.StandardButton.Ok
            )
            self.close()

    def clearCart(self):
        if cartItems != []:
            button = self.sender()
            if button:
                row = self.cart.currentRow()

                button = QMessageBox.critical(
                    self,
                    'Clear Cart',
                    'Are you sure that you want to clear cart?',
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No
                )

                if button == QMessageBox.StandardButton.Yes:
                    self.cart.clearContents()

                    try:
                        query = "DELETE FROM cart"
                        mycursor.execute(query)
                        db.commit()
                    except:
                        QMessageBox.critical(
                            self,
                            'Failed - Database error occurred',
                            'Cart Clear Failed',
                            QMessageBox.StandardButton.Ok
                        )

                    self.amount.setText(str(0))

                    msg = QMessageBox.information(
                        self,
                        'Success',
                        'Cart Cleared Successfully',
                        QMessageBox.StandardButton.Ok
                    )
                    if msg == QMessageBox.StandardButton.Ok:
                        self.close()

        else:
            button = QMessageBox.information(
                self,
                'Empty Cart',
                'No Item In Cart',
                QMessageBox.StandardButton.Ok
            )
            if button == QMessageBox.StandardButton.Ok:
                self.close()

    def deleteClicked(self):
        row = self.cart.currentIndex().row()
        item_id = self.cart.item(row, 0).text()
        quantity = self.cart.item(row, 2).text()
        price = self.cart.item(row, 3).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Delete this item from cart?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.cart.removeRow(row)

            item_total = int(price) * int(quantity)
            self.total -= item_total

            self.amount.setText(str(self.total))

            try:
                query = "DELETE FROM cart WHERE CartID = ?"
                mycursor.execute(query, (item_id,))

                db.commit()
                print("Product deleted successfully")

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Product deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.critical(
                    self,
                    'Failed',
                    'Delete Item Failed',
                    QMessageBox.StandardButton.Ok
                )
class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi('./UIs/login.ui', self)
        self.loginbtn.clicked.connect(self.login)

    def login(self):
        global username
        global password

        username = self.name.text()
        password = self.password.text()

        def admin(self):
            home = AdminDashboard()
            widget.addWidget(home)
            widget.setCurrentIndex(widget.currentIndex()+1)
        def sales(self):
            home = SalesAttendantDashboard()
            widget.addWidget(home)
            widget.setCurrentIndex(widget.currentIndex()+1)
        def store(self):
            home = StoreOfficerDashboard()
            widget.addWidget(home)
            widget.setCurrentIndex(widget.currentIndex()+1)

        try:
            query = "SELECT role FROM users where password = ? and username = ?"
            results = mycursor.execute(query, (password, username)).fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error occurred',
                'Find User Failed Failed',
                QMessageBox.StandardButton.Ok
            )
                            

        if results == []:
            QMessageBox.warning(
                self,
                'Failed',
                'Invalid username or password',
                QMessageBox.StandardButton.Ok
            )
            self.password.setText("")
        elif 'admin' in results[0]:
            admin(self)
        elif 'store' in results[0]:
            store(self)
        elif 'sales' in results[0]:
            sales(self)
class Register(QDialog):
    def __init__(self):
        super(Register, self).__init__()
        loadUi('./UIs/signup.ui', self)
        self.signupbtn.clicked.connect(self.signup)
        self.upload.clicked.connect(self.uploadFile)

    def uploadFile(self):
        self.file = QFileDialog.getOpenFileName(self, "Upload Image", 'c:/Users', "Image files(*.jpg *png)")
        self.filename.setText(self.file[0])


    def signup(self):
        global username
        global password

        fullname = self.fullname.text()
        username = self.username.text()
        email = self.email.text()
        confirm = self.confirm.text()
        password = self.password.text()

        if password == confirm:
            try:
                query = "INSERT INTO users (username,name,email,password,image) VALUES(?,?,?,?,?)"
                mycursor.execute(query, (username,fullname,email,password,self.file[0]))
                db.commit()

                home = AdminDashboard()
                widget.addWidget(home)
                widget.setCurrentIndex(widget.currentIndex()+1)
            except:
                QMessageBox.warning(
                    self,
                    'Failed',
                    'User Already Exists',
                    QMessageBox.StandardButton.Ok
                )

        else:
            QMessageBox.warning(
                self,
                'Failed',
                'Passwords do not match',
                QMessageBox.StandardButton.Ok
            )
#######END - PUBLIC########




#######START - SALES ATTENDANT########
class SalesAttendantDashboard(QMainWindow):
    def __init__(self):
        super(SalesAttendantDashboard, self).__init__()
        loadUi('./UIs/sales_dashboard.ui', self)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        try:
            self.products = mycursor.execute("SELECT * FROM supplier").fetchall()
            self.customer = mycursor.execute("SELECT * FROM customer").fetchall()
            self.cart = mycursor.execute("SELECT * FROM cart").fetchall()
            self.amounts = mycursor.execute("SELECT Total_Amount FROM purchase").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Dashboard Values Failed',
                QMessageBox.StandardButton.Ok
            ) 

        try:
            self.report = mycursor.execute("SELECT * FROM report").fetchall()
            print(self.report)
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Products Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['Item', 'Quantity', 'DateTime']

        self.report_one.setColumnCount(3)
        self.report_one.setColumnWidth(0, 100)
        self.report_one.setColumnWidth(1, 80)
        self.report_one.setColumnWidth(2, 200)

        self.report_one.setHorizontalHeaderLabels(label)
        self.report_one.setRowCount(len(self.report))

        row = 0
        for e in self.report:
            self.report_one.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.report_one.setItem(row, 1, QTableWidgetItem(str(e[1])))
            self.report_one.setItem(row, 2, QTableWidgetItem(str(e[2])))
            row+=1

        total_amount = 0
        for amount in self.amounts:
            total_amount += amount[0]

        self.product.setText(str(len(self.products)))
        self.customers_2.setText(str(len(self.customer)))
        self.cart_2.setText(str(len(self.cart)))

    # def plot(self, hour, temperature):
    #     self.graphWidget.plot(hour, temperature)
    #     self.graphWidget.setTitle("Monthly Sales")
    #     self.graphWidget.setLabel('left', 'Sales', color='red', size=40)
    #     self.graphWidget.setLabel('bottom', 'Month', color='red', size=40)

    def dashboards(self):
        home = SalesAttendantDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = SalesAttendantProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = SalesAttendantCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = SalesAttendantPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
    def supplier(self):
        suppliers = SalesAttendantSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class SalesAttendantPurchases(QMainWindow):
    def __init__(self):
        super(SalesAttendantPurchases, self).__init__()
        loadUi('./UIs/sales_purchase.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            rows = mycursor.execute("SELECT * FROM purchase").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Purchases Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['ID','Items', 'Total Amount', 'Amount Paid', 'Balance', 'DateTime', 'Delete']

        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 250)

        self.table.setHorizontalHeaderLabels(label)
        self.table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.table.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(e[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(e[2])))
            self.table.setItem(row, 3, QTableWidgetItem(str(e[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e[4])))
            self.table.setItem(row, 5, QTableWidgetItem(str(e[5])))
            row += 1
    
    def searchs(self, words):
        self.table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def dashboards(self):
        home = SalesAttendantDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = SalesAttendantProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = SalesAttendantCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = SalesAttendantPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
    def supplier(self):
        suppliers = SalesAttendantSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class SalesAttendantProducts(QMainWindow):
    def __init__(self):
        super(SalesAttendantProducts, self).__init__()
        loadUi('./UIs/sales_product.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)
        self.viewCart.clicked.connect(self.executeViewCart)

        try:
            self.rows = mycursor.execute("SELECT * FROM product INNER JOIN category USING(CategoryID)").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Products Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['ID', 'Name', 'Description', 'Quantity', 'Unit Price', 'Category', 'Delete']

        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 10)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 300)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 250)

        self.table.setHorizontalHeaderLabels(label)
        self.table.setRowCount(len(self.rows))

        row = 0
        for e in self.rows:
            self.table.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.table.setItem(row, 1, QTableWidgetItem(e[1]))
            self.table.setItem(row, 2, QTableWidgetItem(e[2]))
            self.table.setItem(row, 3, QTableWidgetItem(str(e[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e[4])))
            self.table.setItem(row, 5, QTableWidgetItem(str(e[6])))
            row += 1

        self.table.cellClicked.connect(self.addToCart)
        
    def searchs(self, words):
        self.table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def executeViewCart(self):
        try:
            row = mycursor.execute("SELECT * FROM cart").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Cart Items Failed',
                QMessageBox.StandardButton.Ok
            )
        if row != []:
            view_cart = ViewCart()
            view_cart.setWindowTitle("Cart")
            view_cart.setWindowIcon(QIcon('./icons/cart-line-icon.png'))
            view_cart.exec()
        else:
            QMessageBox.warning(
                self,
                'Cart',
                'No Item In Cart',
                QMessageBox.StandardButton.Ok
            )

    def addToCart(self):
        row = self.table.currentRow()
        col = self.table.currentColumn()
        button = QMessageBox.question(
            self,
            'Add to cart',
            'Add this item to cart?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if button == QMessageBox.StandardButton.Yes:
            item = self.table.item(row, 1).text()

            query = "SELECT ProductID,Quantity FROM product WHERE ProductName = ?"
            row = mycursor.execute(query, (item,)).fetchone()
            product_id = row[0]
            global product_quantity
            product_quantity = row[1]

            AddToCart(product_id).exec()

    def dashboards(self):
        home = SalesAttendantDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = SalesAttendantProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = SalesAttendantCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = SalesAttendantPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
    def supplier(self):
        suppliers = SalesAttendantSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class SalesAttendantCustomers(QMainWindow):
    def __init__(self):
        super(SalesAttendantCustomers, self).__init__()
        loadUi('./UIs/sales_customer.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddCustomer)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            rows = mycursor.execute("SELECT * FROM customer").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Phone', 'Email', 'Business name', 'Delete'
        ]

        self.customer_table.setColumnCount(5)
        self.customer_table.setColumnWidth(0, 250)
        self.customer_table.setColumnWidth(1, 150)
        self.customer_table.setColumnWidth(2, 250)
        self.customer_table.setColumnWidth(3, 300)
        self.customer_table.setColumnWidth(4, 80)

        self.customer_table.setHorizontalHeaderLabels(label)
        self.customer_table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)
            self.customer_table.setItem(row, 0, QTableWidgetItem(e[1]))
            self.customer_table.setItem(row, 1, QTableWidgetItem(e[2]))
            self.customer_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            self.customer_table.setItem(row, 3, QTableWidgetItem(str(e[4])))
            self.customer_table.setCellWidget(row, 4, self.delete_btn)
            row += 1

    def executeAddCustomer(self):
        add_customer = AddCustomer(self.customer_table, self.deleteClicked)
        add_customer.setWindowTitle("Add Customer")
        add_customer.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_customer.exec()

    def searchs(self, words):
        self.customer_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.customer_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.customer_table.currentRow()
        item = self.customer_table.item(row, 0).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this customer?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.customer_table.removeRow(row)

            try: 
                try:
                    query = "DELETE FROM customer WHERE CustomerName = ?"
                    mycursor.execute(query, (item,))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error',
                        'Delete Customer Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Customer deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.warning(
                    self,
                    'Failed!',
                    'Delete customer failed',
                    QMessageBox.StandardButton.Ok
                )

    def dashboards(self):
        home = SalesAttendantDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = SalesAttendantProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = SalesAttendantCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = SalesAttendantPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
    def supplier(self):
        suppliers = SalesAttendantSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class SalesAttendantSuppliers(QMainWindow):
    def __init__(self):
        super(SalesAttendantSuppliers, self).__init__()
        loadUi('./UIs/sales_supplier.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddSupplier)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            result = mycursor.execute("SELECT * FROM supplier").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Phone', 'Email'
        ]

        self.suppliers_table.setColumnCount(3)
        self.suppliers_table.setColumnWidth(0, 250)
        self.suppliers_table.setColumnWidth(1, 150)
        self.suppliers_table.setColumnWidth(2, 250)

        self.suppliers_table.setHorizontalHeaderLabels(label)
        self.suppliers_table.setRowCount(len(result))

        row = 0
        for e in result:
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(e[1]))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(e[2]))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            row += 1

    def executeAddSupplier(self):
        add_supplier = AddSupplier(self.suppliers_table, self.deleteClicked)
        add_supplier.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_supplier.exec()

    def searchs(self, words):
        self.suppliers_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.suppliers_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.suppliers_table.currentRow()
        item = self.suppliers_table.item(row, 0).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this supplier?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.suppliers_table.removeRow(row)

            try: 
                try:
                    query = "DELETE FROM supplier WHERE SupplierName = ?"
                    mycursor.execute(query, (item,))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error',
                        'Delete Supplier Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Supplier deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.warning(
                    self,
                    'Failed!',
                    'Delete Supplier failed',
                    QMessageBox.StandardButton.Ok
                )

    def dashboards(self):
        home = SalesAttendantDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = SalesAttendantProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = SalesAttendantCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = SalesAttendantPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
    def supplier(self):
        suppliers = SalesAttendantSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
#######END - SALES ATTENDANT########


#######START - STORE OFFICER########
class StoreOfficerDashboard(QMainWindow):
    def __init__(self):
        super(StoreOfficerDashboard, self).__init__()
        loadUi('./UIs/store_dashboard.ui', self)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        try:
            self.products = mycursor.execute("SELECT * FROM supplier").fetchall()
            self.customer = mycursor.execute("SELECT * FROM customer").fetchall()
            self.cart = mycursor.execute("SELECT * FROM purchase").fetchall()
            self.amounts = mycursor.execute("SELECT Total_Amount FROM purchase").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Dashboard Values Failed',
                QMessageBox.StandardButton.Ok
            ) 

        try:
            self.report = mycursor.execute("SELECT * FROM report").fetchall()
            print(self.report)
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Products Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['Item', 'Quantity', 'DateTime']

        self.report_one.setColumnCount(3)
        self.report_one.setColumnWidth(0, 100)
        self.report_one.setColumnWidth(1, 80)
        self.report_one.setColumnWidth(2, 200)

        self.report_one.setHorizontalHeaderLabels(label)
        self.report_one.setRowCount(len(self.report))

        row = 0
        for e in self.report:
            self.report_one.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.report_one.setItem(row, 1, QTableWidgetItem(str(e[1])))
            self.report_one.setItem(row, 2, QTableWidgetItem(str(e[2])))
            row+=1

        total_amount = 0
        for amount in self.amounts:
            total_amount += amount[0]

        self.product.setText(str(len(self.products)))
        self.customers_2.setText(str(len(self.customer)))
        self.cart_2.setText(str(len(self.cart)))

    # def plot(self, hour, temperature):
    #     self.graphWidget.plot(hour, temperature)
    #     self.graphWidget.setTitle("Monthly Sales")
    #     self.graphWidget.setLabel('left', 'Sales', color='red', size=40)
    #     self.graphWidget.setLabel('bottom', 'Month', color='red', size=40)

    def dashboards(self):
        home = StoreOfficerDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = StoreOfficerProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = StoreOfficerCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = StoreOfficerSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = StoreOfficerPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class StoreOfficerProducts(QMainWindow):
    def __init__(self):
        super(StoreOfficerProducts, self).__init__()
        loadUi('./UIs/store_product.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        self.add_product.clicked.connect(self.executeAddProduct)
        self.add_category.clicked.connect(self.executeAddCategory)

        try:
            self.rows = mycursor.execute("SELECT * FROM product INNER JOIN category USING(CategoryID)").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Products Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['ID', 'Name', 'Description', 'Quantity', 'Unit Price', 'Category', 'Delete']

        self.table.setColumnCount(7)
        self.table.setColumnWidth(0, 10)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 300)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 250)
        self.table.setColumnWidth(6, 70)

        self.table.setHorizontalHeaderLabels(label)
        self.table.setRowCount(len(self.rows))

        row = 0
        for e in self.rows:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)

            self.table.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.table.setItem(row, 1, QTableWidgetItem(e[1]))
            self.table.setItem(row, 2, QTableWidgetItem(e[2]))
            self.table.setItem(row, 3, QTableWidgetItem(str(e[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e[4])))
            self.table.setItem(row, 5, QTableWidgetItem(str(e[6])))
            self.table.setCellWidget(row, 6, self.delete_btn)
            row += 1
        

    def executeAddProduct(self):
        try:
            category_rows = mycursor.execute("SELECT * FROM category").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Categories Failed',
                QMessageBox.StandardButton.Ok
            )
        if category_rows != []:
            add_prod = AddProduct(self.table, self.deleteClicked)
            add_prod.setWindowTitle("Add Product")
            add_prod.setWindowIcon(QIcon('./icons/groceries-icon.png'))
            add_prod.exec()
        else:
            QMessageBox.critical(
                self,
                'No Category',
                'Please add a category',
                QMessageBox.StandardButton.Ok
            )

    def searchs(self, words):
        self.table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def executeAddCategory(self):
        add_cat = AddCategory()
        add_cat.setWindowTitle("Add Category")
        add_cat.setWindowIcon(QIcon('./icons/add-item-in-cart-icon.png'))
        add_cat.exec()

    def deleteClicked(self):
        row = self.table.currentRow()
        item = self.table.item(row, 1).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete the selected row?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)

            query = "DELETE FROM product WHERE ProductName = ?"
            mycursor.execute(query, (item,))

            db.commit()
            print("Product deleted successfully")

            button = QMessageBox.information(
                self,
                'Successful',
                'Product deleted successfully',
                QMessageBox.StandardButton.Ok
            )
            
    def dashboards(self):
        home = StoreOfficerDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = StoreOfficerProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = StoreOfficerCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = StoreOfficerSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = StoreOfficerPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class StoreOfficerPurchases(QMainWindow):
    def __init__(self):
        super(StoreOfficerPurchases, self).__init__()
        loadUi('./UIs/store_purchase.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            rows = mycursor.execute("SELECT * FROM purchase").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Purchases Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['ID','Items', 'Total Amount', 'Amount Paid', 'Balance', 'DateTime']

        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 250)

        self.table.setHorizontalHeaderLabels(label)
        self.table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.table.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(e[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(e[2])))
            self.table.setItem(row, 3, QTableWidgetItem(str(e[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e[4])))
            self.table.setItem(row, 5, QTableWidgetItem(str(e[5])))
            row += 1
    
    def searchs(self, words):
        self.table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)


    def dashboards(self):
        home = StoreOfficerDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = StoreOfficerProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = StoreOfficerCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = StoreOfficerSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = StoreOfficerPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class StoreOfficerCustomers(QMainWindow):
    def __init__(self):
        super(StoreOfficerCustomers, self).__init__()
        loadUi('./UIs/store_customer.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddCustomer)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            rows = mycursor.execute("SELECT * FROM customer").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Phone', 'Email', 'Business name', 'Delete'
        ]

        self.customer_table.setColumnCount(5)
        self.customer_table.setColumnWidth(0, 250)
        self.customer_table.setColumnWidth(1, 150)
        self.customer_table.setColumnWidth(2, 250)
        self.customer_table.setColumnWidth(3, 300)
        self.customer_table.setColumnWidth(4, 80)

        self.customer_table.setHorizontalHeaderLabels(label)
        self.customer_table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)
            self.customer_table.setItem(row, 0, QTableWidgetItem(e[1]))
            self.customer_table.setItem(row, 1, QTableWidgetItem(e[2]))
            self.customer_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            self.customer_table.setItem(row, 3, QTableWidgetItem(str(e[4])))
            self.customer_table.setCellWidget(row, 4, self.delete_btn)
            row += 1

    def executeAddCustomer(self):
        add_customer = AddCustomer(self.customer_table, self.deleteClicked)
        add_customer.setWindowTitle("Add Customer")
        add_customer.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_customer.exec()

    def searchs(self, words):
        self.customer_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.customer_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.customer_table.currentRow()
        item = self.customer_table.item(row, 0).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this customer?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.customer_table.removeRow(row)

            try: 
                try:
                    query = "DELETE FROM customer WHERE CustomerName = ?"
                    mycursor.execute(query, (item,))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error',
                        'Delete Customer Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Customer deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.warning(
                    self,
                    'Failed!',
                    'Delete customer failed',
                    QMessageBox.StandardButton.Ok
                )

    def dashboards(self):
        home = StoreOfficerDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = StoreOfficerProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = StoreOfficerCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = StoreOfficerSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = StoreOfficerPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
class StoreOfficerSuppliers(QMainWindow):
    def __init__(self):
        super(StoreOfficerSuppliers, self).__init__()
        loadUi('./UIs/store_supplier.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddSupplier)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.productss)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            result = mycursor.execute("SELECT * FROM supplier").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Phone', 'Email', 'Delete'
        ]

        self.suppliers_table.setColumnCount(4)
        self.suppliers_table.setColumnWidth(0, 250)
        self.suppliers_table.setColumnWidth(1, 150)
        self.suppliers_table.setColumnWidth(2, 250)
        self.suppliers_table.setColumnWidth(3, 80)

        self.suppliers_table.setHorizontalHeaderLabels(label)
        self.suppliers_table.setRowCount(len(result))

        row = 0
        for e in result:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(e[1]))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(e[2]))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            self.suppliers_table.setCellWidget(row, 3, self.delete_btn)
            row += 1

    def executeAddSupplier(self):
        add_supplier = AddSupplier(self.suppliers_table, self.deleteClicked)
        add_supplier.setWindowTitle("Add Customer")
        add_supplier.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_supplier.exec()

    def searchs(self, words):
        self.suppliers_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.suppliers_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.suppliers_table.currentRow()
        item = self.suppliers_table.item(row, 0).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this supplier?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.suppliers_table.removeRow(row)

            try: 
                try:
                    query = "DELETE FROM supplier WHERE SupplierName = ?"
                    mycursor.execute(query, (item,))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error',
                        'Delete Supplier Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Supplier deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.warning(
                    self,
                    'Failed!',
                    'Delete Supplier failed',
                    QMessageBox.StandardButton.Ok
                )

    def dashboards(self):
        home = StoreOfficerDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = StoreOfficerProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = StoreOfficerCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = StoreOfficerSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = StoreOfficerPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
#######END - STORE OFFICER########



#######START - ADMIN########
class AdminDashboard(QMainWindow):
    def __init__(self):
        super(AdminDashboard, self).__init__()
        loadUi('./UIs/dashboard.ui', self)

        self.dashboard.clicked.connect(self.dashboardss)
        self.products.clicked.connect(self.productss)
        self.customers.clicked.connect(self.customer)
        self.suppliers.clicked.connect(self.supplier)
        self.cart.clicked.connect(self.purchase)
        self.users_2.clicked.connect(self.user)
        self.logout.clicked.connect(self.login)

        # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        try:
            self.products = mycursor.execute("SELECT * FROM supplier").fetchall()
            self.customer = mycursor.execute("SELECT * FROM customer").fetchall()
            self.cart = mycursor.execute("SELECT * FROM purchase").fetchall()
            self.amounts = mycursor.execute("SELECT Total_Amount FROM purchase").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Dashboard Values Failed',
                QMessageBox.StandardButton.Ok
            ) 

        try:
            self.report = mycursor.execute("SELECT * FROM report").fetchall()
            print(self.report)
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Products Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['Item', 'Quantity', 'DateTime']

        self.report_one.setColumnCount(3)
        self.report_one.setColumnWidth(0, 100)
        self.report_one.setColumnWidth(1, 80)
        self.report_one.setColumnWidth(2, 200)

        self.report_one.setHorizontalHeaderLabels(label)
        self.report_one.setRowCount(len(self.report))

        row = 0
        for e in self.report:
            self.report_one.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.report_one.setItem(row, 1, QTableWidgetItem(str(e[1])))
            self.report_one.setItem(row, 2, QTableWidgetItem(str(e[2])))
            row+=1

        total_amount = 0
        for amount in self.amounts:
            total_amount += amount[0]

        self.product.setText(str(len(self.products)))
        self.customers_2.setText(str(len(self.customer)))
        self.cart_2.setText(str(len(self.cart)))

    # def plot(self, hour, temperature):
    #     self.graphWidget.plot(hour, temperature)
    #     self.graphWidget.setTitle("Monthly Sales")
    #     self.graphWidget.setLabel('left', 'Sales', color='red', size=40)
    #     self.graphWidget.setLabel('bottom', 'Month', color='red', size=40)

    def dashboardss(self):
        home = AdminDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = AdminProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = AdminCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = AdminSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = AdminPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def user(self):
        user = AdminUsers()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)
class AdminProducts(QMainWindow):
    def __init__(self):
        super(AdminProducts, self).__init__()
        loadUi('./UIs/product.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.dashboard.clicked.connect(self.dashboardss)
        self.products.clicked.connect(self.productss)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.users_2.clicked.connect(self.user)
        self.suppliers.clicked.connect(self.supplier)
        self.logout.clicked.connect(self.login)
        self.add_product.clicked.connect(self.executeAddProduct)
        self.add_category.clicked.connect(self.executeAddCategory)

        try:
            self.rows = mycursor.execute("SELECT * FROM product INNER JOIN category USING(CategoryID)").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Products Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['ID', 'Name', 'Description', 'Quantity', 'Unit Price', 'Category', 'Delete']

        self.table.setColumnCount(7)
        self.table.setColumnWidth(0, 10)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 300)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 250)
        self.table.setColumnWidth(6, 70)

        self.table.setHorizontalHeaderLabels(label)
        self.table.setRowCount(len(self.rows))

        row = 0
        for e in self.rows:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)

            self.table.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.table.setItem(row, 1, QTableWidgetItem(e[1]))
            self.table.setItem(row, 2, QTableWidgetItem(e[2]))
            self.table.setItem(row, 3, QTableWidgetItem(str(e[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e[4])))
            self.table.setItem(row, 5, QTableWidgetItem(str(e[6])))
            self.table.setCellWidget(row, 6, self.delete_btn)
            row += 1
        

    def executeAddProduct(self):
        try:
            category_rows = mycursor.execute("SELECT * FROM category").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Categories Failed',
                QMessageBox.StandardButton.Ok
            )
        if category_rows != []:
            add_prod = AddProduct(self.table, self.deleteClicked)
            add_prod.setWindowTitle("Add Product")
            add_prod.setWindowIcon(QIcon('./icons/groceries-icon.png'))
            add_prod.exec()
        else:
            QMessageBox.critical(
                self,
                'No Category',
                'Please add a category',
                QMessageBox.StandardButton.Ok
            )

    def searchs(self, words):
        self.table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def executeAddCategory(self):
        add_cat = AddCategory()
        add_cat.setWindowTitle("Add Category")
        add_cat.setWindowIcon(QIcon('./icons/add-item-in-cart-icon.png'))
        add_cat.exec()

    def deleteClicked(self):
        row = self.table.currentRow()
        item = self.table.item(row, 1).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete the selected row?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.table.removeRow(row)

            query = "DELETE FROM product WHERE ProductName = ?"
            mycursor.execute(query, (item,))

            db.commit()
            print("Product deleted successfully")

            button = QMessageBox.information(
                self,
                'Successful',
                'Product deleted successfully',
                QMessageBox.StandardButton.Ok
            )
            

    def dashboardss(self):
        home = AdminDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def productss(self):
        products = AdminProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = AdminCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = AdminSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = AdminPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def user(self):
        user = AdminUsers()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)
class AdminCustomers(QMainWindow):
    def __init__(self):
        super(AdminCustomers, self).__init__()
        loadUi('./UIs/customer.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddCustomer)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.product)
        self.users_2.clicked.connect(self.user)
        self.customers.clicked.connect(self.customer)
        self.suppliers.clicked.connect(self.supplier)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            rows = mycursor.execute("SELECT * FROM customer").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Phone', 'Email', 'Business name', 'Delete'
        ]

        self.customer_table.setColumnCount(5)
        self.customer_table.setColumnWidth(0, 250)
        self.customer_table.setColumnWidth(1, 150)
        self.customer_table.setColumnWidth(2, 250)
        self.customer_table.setColumnWidth(3, 300)
        self.customer_table.setColumnWidth(4, 80)

        self.customer_table.setHorizontalHeaderLabels(label)
        self.customer_table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)
            self.customer_table.setItem(row, 0, QTableWidgetItem(e[1]))
            self.customer_table.setItem(row, 1, QTableWidgetItem(e[2]))
            self.customer_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            self.customer_table.setItem(row, 3, QTableWidgetItem(str(e[4])))
            self.customer_table.setCellWidget(row, 4, self.delete_btn)
            row += 1

    def executeAddCustomer(self):
        add_customer = AddCustomer(self.customer_table, self.deleteClicked)
        add_customer.setWindowTitle("Add Customer")
        add_customer.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_customer.exec()

    def searchs(self, words):
        self.customer_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.customer_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.customer_table.currentRow()
        item = self.customer_table.item(row, 0).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this customer?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.customer_table.removeRow(row)

            try: 
                try:
                    query = "DELETE FROM customer WHERE CustomerName = ?"
                    mycursor.execute(query, (item,))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error',
                        'Delete Customer Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Customer deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.warning(
                    self,
                    'Failed!',
                    'Delete customer failed',
                    QMessageBox.StandardButton.Ok
                )

    def dashboards(self):
        home = AdminDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def product(self):
        products = AdminProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = AdminCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = AdminSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = AdminPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def user(self):
        user = AdminUsers()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)
class AdminSuppliers(QMainWindow):
    def __init__(self):
        super(AdminSuppliers, self).__init__()
        loadUi('./UIs/supplier.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddSupplier)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.product)
        self.users_2.clicked.connect(self.user)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            result = mycursor.execute("SELECT * FROM supplier").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Phone', 'Email', 'Delete'
        ]

        self.suppliers_table.setColumnCount(4)
        self.suppliers_table.setColumnWidth(0, 250)
        self.suppliers_table.setColumnWidth(1, 150)
        self.suppliers_table.setColumnWidth(2, 250)
        self.suppliers_table.setColumnWidth(3, 80)

        self.suppliers_table.setHorizontalHeaderLabels(label)
        self.suppliers_table.setRowCount(len(result))

        row = 0
        for e in result:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(e[1]))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(e[2]))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            self.suppliers_table.setCellWidget(row, 3, self.delete_btn)
            row += 1

    def executeAddSupplier(self):
        add_supplier = AddSupplier(self.suppliers_table, self.deleteClicked)
        add_supplier.setWindowTitle("Add Customer")
        add_supplier.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_supplier.exec()

    def searchs(self, words):
        self.suppliers_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.suppliers_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.suppliers_table.currentRow()
        item = self.suppliers_table.item(row, 0).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this supplier?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.suppliers_table.removeRow(row)

            try: 
                try:
                    query = "DELETE FROM supplier WHERE SupplierName = ?"
                    mycursor.execute(query, (item,))
                    db.commit()
                except:
                    QMessageBox.critical(
                        self,
                        'Failed - Database error',
                        'Delete Supplier Failed',
                        QMessageBox.StandardButton.Ok
                    )

                button = QMessageBox.information(
                    self,
                    'Successful',
                    'Supplier deleted successfully',
                    QMessageBox.StandardButton.Ok
                )
            except:
                button = QMessageBox.warning(
                    self,
                    'Failed!',
                    'Delete Supplier failed',
                    QMessageBox.StandardButton.Ok
                )

    def dashboards(self):
        home = AdminDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def product(self):
        products = AdminProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = AdminCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def supplier(self):
        suppliers = AdminSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = AdminPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def user(self):
        user = AdminUsers()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)
class AdminUsers(QMainWindow):
    def __init__(self):
        super(AdminUsers, self).__init__()
        loadUi('./UIs/user.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.add_new_cat_2.clicked.connect(self.executeAddUser)

        self.dashboard.clicked.connect(self.dashboards)
        self.products.clicked.connect(self.product)
        self.customers.clicked.connect(self.customer)
        self.suppliers.clicked.connect(self.supplier)
        self.users_2.clicked.connect(self.user)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            query = "SELECT * FROM users WHERE username != ?"
            rows = mycursor.execute(query, (username,)).fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Customers Failed',
                QMessageBox.StandardButton.Ok
            )

        label = [
            'Name', 'Username', 'Email', 'Password', 'Role', 'Delete'
        ]

        self.users_table.setColumnCount(6)
        self.users_table.setColumnWidth(0, 250)
        self.users_table.setColumnWidth(1, 150)
        self.users_table.setColumnWidth(2, 200)
        self.users_table.setColumnWidth(3, 150)
        self.users_table.setColumnWidth(4, 100)
        self.users_table.setColumnWidth(5, 80)

        self.users_table.setHorizontalHeaderLabels(label)
        self.users_table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.delete_btn = QPushButton('delete')
            self.delete_btn.setIcon(QIcon('./icons/recycle-bin-line-icon.png'))
            self.delete_btn.setStyleSheet('QPushButton { background-color:  rgb(170, 0, 0); color: #fff }')
            self.delete_btn.clicked.connect(self.deleteClicked)
            self.users_table.setItem(row, 0, QTableWidgetItem(e[2]))
            self.users_table.setItem(row, 1, QTableWidgetItem(e[1]))
            self.users_table.setItem(row, 2, QTableWidgetItem(str(e[3])))
            self.users_table.setItem(row, 3, QTableWidgetItem(str(e[4])))
            self.users_table.setItem(row, 4, QTableWidgetItem(str(e[6])))
            self.users_table.setCellWidget(row, 5, self.delete_btn)
            row += 1

    def executeAddUser(self):
        add_user = AddUser(self.users_table, self.deleteClicked)
        add_user.setWindowTitle("Add User")
        add_user.setWindowIcon(QIcon('./icons/followers-friends-icon.png'))
        add_user.exec()

    def searchs(self, words):
        self.users_table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.users_table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)

    def deleteClicked(self):
        row = self.users_table.currentRow()
        user = self.users_table.item(row, 1).text()

        button = QMessageBox.critical(
            self,
            'Delete item',
            'Are you sure that you want to delete this user?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if button == QMessageBox.StandardButton.Yes:
            self.users_table.removeRow(row)

            try:
                query = "DELETE FROM users WHERE username = ?"
                mycursor.execute(query, (user,))
                db.commit()
            except:
                QMessageBox.critical(
                    self,
                    'Failed - Database error',
                    'Delete Customer Failed',
                    QMessageBox.StandardButton.Ok
                )

            QMessageBox.information(
                self,
                'Successful',
                'User deleted successfully',
                QMessageBox.StandardButton.Ok
            )

    def dashboards(self):
        home = AdminDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def product(self):
        products = AdminProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = AdminCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = AdminSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = AdminPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def user(self):
        user = AdminUsers()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)
class AdminPurchases(QMainWindow):
    def __init__(self):
        super(AdminPurchases, self).__init__()
        loadUi('./UIs/purchase.ui', self)

        self.search.textChanged.connect(self.searchs)

        try:
            query = "SELECT name,image,role FROM users where password = ? and username = ?"
            self.result = mycursor.execute(query, (password, username)).fetchone()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Find User Failed',
                QMessageBox.StandardButton.Ok
            )

        self.username.setText(str(self.result[0]))
        pic = QPixmap(self.result[1])
        self.image.setPixmap(pic)

        self.dashboard.clicked.connect(self.dashboardss)
        self.products.clicked.connect(self.product)
        self.users_2.clicked.connect(self.user)
        self.suppliers.clicked.connect(self.supplier)
        self.customers.clicked.connect(self.customer)
        self.cart.clicked.connect(self.purchase)
        self.logout.clicked.connect(self.login)

        try:
            rows = mycursor.execute("SELECT * FROM purchase").fetchall()
        except:
            QMessageBox.critical(
                self,
                'Failed - Database error',
                'Get Purchases Failed',
                QMessageBox.StandardButton.Ok
            )

        label = ['ID','Items', 'Total Amount', 'Amount Paid', 'Balance', 'DateTime', 'Delete']

        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 250)

        self.table.setHorizontalHeaderLabels(label)
        self.table.setRowCount(len(rows))

        row = 0
        for e in rows:
            self.table.setItem(row, 0, QTableWidgetItem(str(e[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(e[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(e[2])))
            self.table.setItem(row, 3, QTableWidgetItem(str(e[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(e[4])))
            self.table.setItem(row, 5, QTableWidgetItem(str(e[5])))
            row += 1
    
    def searchs(self, words):
        self.table.setCurrentItem(None)

        if not words:
            return
        matching_items = self.table.findItems(words, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)


    def dashboardss(self):
        home = AdminDashboard()
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def product(self):
        products = AdminProducts()
        widget.addWidget(products)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def customer(self):
        customers = AdminCustomers()
        widget.addWidget(customers)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def supplier(self):
        suppliers = AdminSuppliers()
        widget.addWidget(suppliers)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def purchase(self):
        purchase = AdminPurchases()
        widget.addWidget(purchase)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def login(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def user(self):
        user = AdminUsers()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)
#######END - ADMIN########





    












#main
app = QApplication(sys.argv)
if users != []:
    welcome = LoginScreen()
else:
    welcome = Register()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setWindowTitle("S.T.E.P.S")
widget.setMinimumWidth(1000)
widget.setMinimumHeight(700)
widget.setWindowIcon(QIcon('./icons/point-of-sale.png'))
# widget.setFixedWidth(1200)
# widget.showFullScreen()
widget.show()

try:
    sys.exit(app.exec())
except SystemExit:
    print("Closing Window")    